package com.heimdall.controller;

import com.heimdall.dto.AnalysisJobResponse;
import com.heimdall.entity.AnalysisJob;
import com.heimdall.service.AnalysisOrchestratorService;
import com.heimdall.service.AnalysisJobService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/analysis/jobs")
@RequiredArgsConstructor
@Slf4j
public class AnalysisJobController {

    private final AnalysisJobService analysisJobService;
    private final AnalysisOrchestratorService analysisOrchestratorService;

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
    public ResponseEntity<AnalysisJobResponse> redrive(@PathVariable UUID jobId) {
        AnalysisOrchestratorService.OrchestrationResult result =
            analysisOrchestratorService.redriveJob(jobId, null);
        return ResponseEntity.accepted().body(toResponse(result.job()));
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
