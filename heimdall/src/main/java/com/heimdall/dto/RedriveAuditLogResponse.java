package com.heimdall.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Response DTO for redrive audit log entries.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RedriveAuditLogResponse {
    private Long id;
    private UUID jobId;
    private String idempotencyKey;
    private String previousStatus;
    private Integer previousAttemptCount;
    private String performedBy;
    private LocalDateTime performedAt;
    private String sourceIp;
    private String traceId;
    private String reason;
    private String outcome;
    private String errorMessage;
}
