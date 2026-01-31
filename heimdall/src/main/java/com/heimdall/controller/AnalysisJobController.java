package com.heimdall.controller;

import com.heimdall.dto.AnalysisJobResponse;
import com.heimdall.dto.RedriveAuditLogResponse;
import com.heimdall.dto.RedriveRequest;
import com.heimdall.entity.AnalysisJob;
import com.heimdall.entity.RedriveAuditLog;
import com.heimdall.service.AnalysisOrchestratorService;
import com.heimdall.service.AnalysisJobService;
import com.heimdall.service.RedriveAuditService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/analysis/jobs")
@RequiredArgsConstructor
@Slf4j
public class AnalysisJobController {

    private static final int REDRIVE_RATE_LIMIT = 10;  // max redrives per user
    private static final int REDRIVE_RATE_WINDOW_MINUTES = 60;  // time window

    private final AnalysisJobService analysisJobService;
    private final AnalysisOrchestratorService analysisOrchestratorService;
    private final RedriveAuditService redriveAuditService;

    @GetMapping("/{jobId}")
    public ResponseEntity<AnalysisJobResponse> getJob(@PathVariable UUID jobId) {
        AnalysisJob job = analysisJobService.get(jobId);
        return ResponseEntity.ok(toResponse(job));
    }

    @GetMapping("/failed")
    public ResponseEntity<Page<AnalysisJobResponse>> listFailed(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        Page<AnalysisJobResponse> results = analysisJobService
            .listFailed(PageRequest.of(page, size))
            .map(this::toResponse);
        return ResponseEntity.ok(results);
    }

    @PostMapping("/{jobId}/redrive")
    public ResponseEntity<AnalysisJobResponse> redrive(
        @PathVariable UUID jobId,
        @RequestBody(required = false) RedriveRequest request,
        HttpServletRequest httpRequest
    ) {
        String performedBy = getCurrentUser();
        String sourceIp = getClientIp(httpRequest);
        String userAgent = httpRequest.getHeader("User-Agent");
        String traceId = httpRequest.getHeader("X-Trace-Id");
        String reason = request != null ? request.getReason() : null;

        // Rate limit check
        if (!redriveAuditService.checkRateLimit(performedBy, REDRIVE_RATE_LIMIT, REDRIVE_RATE_WINDOW_MINUTES)) {
            log.warn("Redrive rate limit exceeded: user={}, jobId={}", performedBy, jobId);
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build();
        }

        try {
            // Get job before redrive for audit logging
            AnalysisJob jobBefore = analysisJobService.get(jobId);

            AnalysisOrchestratorService.OrchestrationResult result =
                analysisOrchestratorService.redriveJob(jobId, traceId);

            // Record audit log based on outcome
            if (result.created()) {
                redriveAuditService.recordSuccess(
                    result.job(), performedBy, sourceIp, userAgent, traceId, reason
                );
            } else {
                redriveAuditService.recordSkipped(
                    result.job(), performedBy, sourceIp, userAgent, traceId, reason
                );
            }

            return ResponseEntity.accepted().body(toResponse(result.job()));

        } catch (Exception e) {
            // Record failed attempt
            AnalysisJob job = null;
            try {
                job = analysisJobService.get(jobId);
            } catch (Exception ignored) {}

            redriveAuditService.recordFailure(
                jobId,
                job != null ? job.getIdempotencyKey() : null,
                job != null && job.getStatus() != null ? job.getStatus().name() : null,
                job != null ? job.getAttemptCount() : null,
                performedBy,
                sourceIp,
                userAgent,
                traceId,
                reason,
                e.getMessage()
            );

            throw e;
        }
    }

    /**
     * Get redrive audit history for a specific job.
     */
    @GetMapping("/{jobId}/redrive/audit")
    public ResponseEntity<List<RedriveAuditLogResponse>> getRedriveAuditHistory(@PathVariable UUID jobId) {
        List<RedriveAuditLog> auditLogs = redriveAuditService.getAuditHistoryForJob(jobId);
        List<RedriveAuditLogResponse> response = auditLogs.stream()
            .map(this::toAuditResponse)
            .toList();
        return ResponseEntity.ok(response);
    }

    /**
     * Get all recent redrive audit logs (admin endpoint).
     */
    @GetMapping("/redrive/audit")
    public ResponseEntity<Page<RedriveAuditLogResponse>> getRecentRedriveAudits(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        Page<RedriveAuditLogResponse> response = redriveAuditService
            .getRecentAuditLogs(PageRequest.of(page, size))
            .map(this::toAuditResponse);
        return ResponseEntity.ok(response);
    }

    private String getCurrentUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getName() != null) {
            return auth.getName();
        }
        return "anonymous";
    }

    private String getClientIp(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }

    private RedriveAuditLogResponse toAuditResponse(RedriveAuditLog audit) {
        return RedriveAuditLogResponse.builder()
            .id(audit.getId())
            .jobId(audit.getJobId())
            .idempotencyKey(audit.getIdempotencyKey())
            .previousStatus(audit.getPreviousStatus())
            .previousAttemptCount(audit.getPreviousAttemptCount())
            .performedBy(audit.getPerformedBy())
            .performedAt(audit.getPerformedAt())
            .sourceIp(audit.getSourceIp())
            .traceId(audit.getTraceId())
            .reason(audit.getReason())
            .outcome(audit.getOutcome().name())
            .errorMessage(audit.getErrorMessage())
            .build();
    }

    private AnalysisJobResponse toResponse(AnalysisJob job) {
        return AnalysisJobResponse.builder()
            .jobId(job.getJobId())
            .idempotencyKey(job.getIdempotencyKey())
            .status(job.getStatus())
            .attemptCount(job.getAttemptCount())
            .createdAt(job.getCreatedAt())
            .startedAt(job.getStartedAt())
            .finishedAt(job.getFinishedAt())
            .traceId(job.getTraceId())
            .logId(job.getLogId())
            .resultRef(job.getResultRef())
            .resultSummary(job.getResultSummary())
            .resultPayload(job.getResultPayload())
            .errorCode(job.getErrorCode())
            .errorMessage(job.getErrorMessage())
            .build();
    }
}
