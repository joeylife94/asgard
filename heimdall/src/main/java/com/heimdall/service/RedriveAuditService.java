package com.heimdall.service;

import com.heimdall.entity.AnalysisJob;
import com.heimdall.entity.RedriveAuditLog;
import com.heimdall.repository.RedriveAuditLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * Service for auditing DLQ redrive operations.
 * Provides comprehensive tracking of who, when, and why redrives occurred.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class RedriveAuditService {

    private final RedriveAuditLogRepository auditLogRepository;

    /**
     * Record a successful redrive operation.
     */
    @Transactional
    public RedriveAuditLog recordSuccess(
        AnalysisJob job,
        String performedBy,
        String sourceIp,
        String userAgent,
        String traceId,
        String reason
    ) {
        RedriveAuditLog auditLog = RedriveAuditLog.builder()
            .jobId(job.getJobId())
            .idempotencyKey(job.getIdempotencyKey())
            .previousStatus(job.getStatus() != null ? job.getStatus().name() : null)
            .previousAttemptCount(job.getAttemptCount())
            .performedBy(performedBy)
            .performedAt(LocalDateTime.now())
            .sourceIp(sourceIp)
            .userAgent(userAgent)
            .traceId(traceId)
            .reason(reason)
            .outcome(RedriveAuditLog.Outcome.SUCCESS)
            .build();

        RedriveAuditLog saved = auditLogRepository.save(auditLog);

        log.info(
            "Redrive audit recorded: jobId={}, performedBy={}, sourceIp={}, traceId={}, outcome=SUCCESS",
            job.getJobId(), performedBy, sourceIp, traceId
        );

        return saved;
    }

    /**
     * Record a failed redrive attempt.
     */
    @Transactional
    public RedriveAuditLog recordFailure(
        UUID jobId,
        String idempotencyKey,
        String previousStatus,
        Integer previousAttemptCount,
        String performedBy,
        String sourceIp,
        String userAgent,
        String traceId,
        String reason,
        String errorMessage
    ) {
        RedriveAuditLog auditLog = RedriveAuditLog.builder()
            .jobId(jobId)
            .idempotencyKey(idempotencyKey)
            .previousStatus(previousStatus)
            .previousAttemptCount(previousAttemptCount)
            .performedBy(performedBy)
            .performedAt(LocalDateTime.now())
            .sourceIp(sourceIp)
            .userAgent(userAgent)
            .traceId(traceId)
            .reason(reason)
            .outcome(RedriveAuditLog.Outcome.FAILED)
            .errorMessage(errorMessage)
            .build();

        RedriveAuditLog saved = auditLogRepository.save(auditLog);

        log.warn(
            "Redrive audit recorded: jobId={}, performedBy={}, sourceIp={}, traceId={}, outcome=FAILED, error={}",
            jobId, performedBy, sourceIp, traceId, errorMessage
        );

        return saved;
    }

    /**
     * Record a skipped redrive (job not in retriable state).
     */
    @Transactional
    public RedriveAuditLog recordSkipped(
        AnalysisJob job,
        String performedBy,
        String sourceIp,
        String userAgent,
        String traceId,
        String reason
    ) {
        RedriveAuditLog auditLog = RedriveAuditLog.builder()
            .jobId(job.getJobId())
            .idempotencyKey(job.getIdempotencyKey())
            .previousStatus(job.getStatus() != null ? job.getStatus().name() : null)
            .previousAttemptCount(job.getAttemptCount())
            .performedBy(performedBy)
            .performedAt(LocalDateTime.now())
            .sourceIp(sourceIp)
            .userAgent(userAgent)
            .traceId(traceId)
            .reason(reason)
            .outcome(RedriveAuditLog.Outcome.SKIPPED)
            .errorMessage("Job status not eligible for redrive: " + job.getStatus())
            .build();

        RedriveAuditLog saved = auditLogRepository.save(auditLog);

        log.info(
            "Redrive audit recorded: jobId={}, performedBy={}, outcome=SKIPPED, reason={}",
            job.getJobId(), performedBy, "Status not eligible"
        );

        return saved;
    }

    /**
     * Get audit history for a specific job.
     */
    public List<RedriveAuditLog> getAuditHistoryForJob(UUID jobId) {
        return auditLogRepository.findByJobIdOrderByPerformedAtDesc(jobId);
    }

    /**
     * Get audit logs for a specific user.
     */
    public Page<RedriveAuditLog> getAuditLogsByUser(String performedBy, Pageable pageable) {
        return auditLogRepository.findByPerformedByOrderByPerformedAtDesc(performedBy, pageable);
    }

    /**
     * Get all recent audit logs (admin view).
     */
    public Page<RedriveAuditLog> getRecentAuditLogs(Pageable pageable) {
        return auditLogRepository.findAllByOrderByPerformedAtDesc(pageable);
    }

    /**
     * Get audit logs within a time range.
     */
    public Page<RedriveAuditLog> getAuditLogsByTimeRange(
        LocalDateTime start,
        LocalDateTime end,
        Pageable pageable
    ) {
        return auditLogRepository.findByTimeRange(start, end, pageable);
    }

    /**
     * Check if a user has exceeded redrive rate limit.
     * Returns true if within allowed limits.
     */
    public boolean checkRateLimit(String performedBy, int maxRedrives, int windowMinutes) {
        LocalDateTime since = LocalDateTime.now().minusMinutes(windowMinutes);
        long count = auditLogRepository.countByPerformedBySince(performedBy, since);
        return count < maxRedrives;
    }

    /**
     * Get failed redrive attempts for troubleshooting.
     */
    public Page<RedriveAuditLog> getFailedRedrives(Pageable pageable) {
        return auditLogRepository.findByOutcomeOrderByPerformedAtDesc(
            RedriveAuditLog.Outcome.FAILED,
            pageable
        );
    }
}
