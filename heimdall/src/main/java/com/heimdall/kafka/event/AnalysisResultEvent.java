package com.heimdall.kafka.event;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalysisResultEvent {

    @Builder.Default
    @JsonProperty("schema_version")
    private int schemaVersion = 1;

    @JsonProperty("job_id")
    @JsonAlias({"requestId", "request_id"})
    private UUID jobId;

    @JsonProperty("status")
    private String status;

    @JsonProperty("summary")
    private String summary;

    @JsonProperty("root_cause")
    private String rootCause;

    @JsonProperty("recommendation")
    private String recommendation;

    @JsonProperty("severity")
    private String severity;

    @JsonProperty("confidence")
    private BigDecimal confidence;

    @JsonProperty("model_used")
    @JsonAlias("model")
    private String modelUsed;

    @JsonProperty("token_usage")
    private TokenUsage tokenUsage;

    @JsonProperty("latency_ms")
    private Long latencyMs;

    @JsonProperty("error_code")
    private String errorCode;

    @JsonProperty("error_message")
    private String errorMessage;

    @JsonProperty("trace_id")
    @JsonAlias({"correlationId", "correlation_id"})
    private String traceId;

    @JsonProperty("log_id")
    @JsonAlias("logId")
    private Long logId;

    // Optional legacy/diagnostic fields
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
    @JsonProperty("timestamp")
    private LocalDateTime timestamp;

    @JsonProperty("result")
    private JsonNode result;
    

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class TokenUsage {
        @JsonProperty("prompt_tokens")
        private Integer promptTokens;
        @JsonProperty("completion_tokens")
        private Integer completionTokens;
        @JsonProperty("total_tokens")
        private Integer totalTokens;
    }
}
