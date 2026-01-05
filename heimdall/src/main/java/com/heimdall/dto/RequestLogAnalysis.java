package com.heimdall.dto;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.validation.constraints.Size;
import lombok.Builder;

@Builder
public record RequestLogAnalysis(
    @Size(max = 200)
    String idempotencyKey,
    JsonNode modelPolicy
) {
}
