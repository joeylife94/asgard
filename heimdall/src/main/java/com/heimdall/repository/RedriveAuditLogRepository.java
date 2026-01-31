package com.heimdall.repository;

import com.heimdall.entity.RedriveAuditLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Repository
public interface RedriveAuditLogRepository extends JpaRepository<RedriveAuditLog, Long> {

    /**
     * Find all redrive attempts for a specific job.
     */
    List<RedriveAuditLog> findByJobIdOrderByPerformedAtDesc(UUID jobId);

    /**
     * Find redrive logs by performer (user).
     */
    Page<RedriveAuditLog> findByPerformedByOrderByPerformedAtDesc(String performedBy, Pageable pageable);

    /**
     * Find redrive logs within a time range.
     */
    @Query("SELECT r FROM RedriveAuditLog r WHERE r.performedAt BETWEEN :start AND :end ORDER BY r.performedAt DESC")
    Page<RedriveAuditLog> findByTimeRange(
        @Param("start") LocalDateTime start,
        @Param("end") LocalDateTime end,
        Pageable pageable
    );

    /**
     * Count redrives by a specific user within a time window (for rate limiting / abuse detection).
     */
    @Query("SELECT COUNT(r) FROM RedriveAuditLog r WHERE r.performedBy = :user AND r.performedAt >= :since")
    long countByPerformedBySince(@Param("user") String user, @Param("since") LocalDateTime since);

    /**
     * Find recent redrive attempts across all jobs (admin view).
     */
    Page<RedriveAuditLog> findAllByOrderByPerformedAtDesc(Pageable pageable);

    /**
     * Find failed redrive attempts (for troubleshooting).
     */
    Page<RedriveAuditLog> findByOutcomeOrderByPerformedAtDesc(RedriveAuditLog.Outcome outcome, Pageable pageable);
}
