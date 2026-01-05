package com.heimdall.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Entity
@Table(
    name = "analysis_jobs",
    indexes = {
        @Index(name = "idx_analysis_jobs_status_created", columnList = "status, created_at"),
        @Index(name = "idx_analysis_jobs_log_id", columnList = "log_id")
    },
    uniqueConstraints = {
        @UniqueConstraint(name = "uk_analysis_jobs_idempotency_key", columnNames = "idempotency_key")
    }
)
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AnalysisJob {

    @Id
    @Column(name = "job_id", nullable = false, updatable = false)
    private UUID jobId;

    @Column(name = "idempotency_key", nullable = false, length = 200)
    private String idempotencyKey;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Status status;

    @Column(name = "attempt_count", nullable = false)
    private int attemptCount;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "finished_at")
    private LocalDateTime finishedAt;

    @Column(name = "trace_id", length = 128)
    private String traceId;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "model_policy", columnDefinition = "json")
    private Map<String, Object> modelPolicy;

    @Column(name = "log_id")
    private Long logId;

    @Column(name = "input_ref", length = 200)
    private String inputRef;

    @Column(name = "result_ref")
    private Long resultRef;

    @Column(name = "result_summary", columnDefinition = "TEXT")
    private String resultSummary;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "result_payload", columnDefinition = "json")
    private Map<String, Object> resultPayload;

    @Column(name = "error_code", length = 100)
    private String errorCode;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @PrePersist
    protected void onCreate() {
        if (jobId == null) {
            jobId = UUID.randomUUID();
        }
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }

    public enum Status {
        PENDING,
        RUNNING,
        SUCCEEDED,
        FAILED
    }
}
