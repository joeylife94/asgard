package com.heimdall.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Audit log for DLQ redrive operations.
 * Tracks who performed redrive, when, and the outcome.
 */
@Entity
@Table(
    name = "redrive_audit_logs",
    indexes = {
        @Index(name = "idx_redrive_audit_job_id", columnList = "job_id"),
        @Index(name = "idx_redrive_audit_performed_at", columnList = "performed_at"),
        @Index(name = "idx_redrive_audit_performed_by", columnList = "performed_by")
    }
)
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RedriveAuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "job_id", nullable = false)
    private UUID jobId;

    @Column(name = "idempotency_key", length = 200)
    private String idempotencyKey;

    @Column(name = "previous_status", length = 20)
    private String previousStatus;

    @Column(name = "previous_attempt_count")
    private Integer previousAttemptCount;

    @Column(name = "performed_by", nullable = false, length = 200)
    private String performedBy;

    @Column(name = "performed_at", nullable = false)
    private LocalDateTime performedAt;

    @Column(name = "source_ip", length = 50)
    private String sourceIp;

    @Column(name = "user_agent", length = 500)
    private String userAgent;

    @Column(name = "trace_id", length = 128)
    private String traceId;

    @Column(name = "reason", length = 500)
    private String reason;

    @Enumerated(EnumType.STRING)
    @Column(name = "outcome", nullable = false, length = 20)
    private Outcome outcome;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @PrePersist
    protected void onCreate() {
        if (performedAt == null) {
            performedAt = LocalDateTime.now();
        }
    }

    public enum Outcome {
        SUCCESS,
        FAILED,
        SKIPPED  // Job was already in non-retriable state
    }
}
