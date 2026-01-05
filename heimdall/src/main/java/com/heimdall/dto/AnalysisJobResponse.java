package com.heimdall.dto;

import com.heimdall.entity.AnalysisJob;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Builder
public record AnalysisJobResponse(
    UUID jobId,
    String idempotencyKey,
    AnalysisJob.Status status,
    int attemptCount,
    LocalDateTime createdAt,
    LocalDateTime startedAt,
    LocalDateTime finishedAt,
    String traceId,
    Long logId,
    Long resultRef,
    String resultSummary,
    Map<String, Object> resultPayload,
    String errorCode,
    String errorMessage
) {
}
