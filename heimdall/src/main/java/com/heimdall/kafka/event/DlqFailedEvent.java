package com.heimdall.kafka.event;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DlqFailedEvent {

    @Builder.Default
    @JsonProperty("schema_version")
    private int schemaVersion = 1;

    @JsonProperty("job_id")
    private UUID jobId;

    @JsonProperty("idempotency_key")
    private String idempotencyKey;

    @JsonProperty("error_code")
    private String errorCode;

    @JsonProperty("error_message")
    private String errorMessage;

    @JsonProperty("trace_id")
    private String traceId;

    @JsonProperty("original_topic")
    private String originalTopic;

    @JsonProperty("original_partition")
    private int originalPartition;

    @JsonProperty("original_offset")
    private long originalOffset;

    @JsonProperty("failed_at")
    private LocalDateTime failedAt;

    @JsonProperty("payload")
    private Map<String, Object> payload;
}
