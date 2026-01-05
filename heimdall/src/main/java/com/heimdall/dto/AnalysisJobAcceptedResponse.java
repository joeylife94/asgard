package com.heimdall.dto;

import com.heimdall.entity.AnalysisJob;
import lombok.Builder;

import java.util.UUID;

@Builder
public record AnalysisJobAcceptedResponse(
    UUID jobId,
    AnalysisJob.Status status,
    boolean created
) {
}
