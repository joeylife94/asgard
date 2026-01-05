package com.heimdall.kafka.event;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalysisRequestEvent {

    @Builder.Default
    @JsonProperty("schema_version")
    private int schemaVersion = 1;

    @JsonProperty("job_id")
    @JsonAlias({"requestId", "request_id"})
    private UUID jobId;

    @JsonProperty("idempotency_key")
    private String idempotencyKey;

    @JsonProperty("log_id")
    @JsonAlias("logId")
    private Long logId;

    @JsonProperty("tenant_id")
    private String tenantId;

    @JsonProperty("priority")
    private String priority;

    @JsonProperty("timeout_ms")
    private Long timeoutMs;

    @JsonProperty("model_policy")
    private JsonNode modelPolicy;

    @JsonProperty("trace_id")
    @JsonAlias({"correlationId", "correlation_id"})
    private String traceId;

    // Optional timestamp retained for debugging/backward compatibility
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
    @JsonProperty("timestamp")
    private LocalDateTime timestamp;
}
