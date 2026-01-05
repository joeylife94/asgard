package com.heimdall.repository;

import com.heimdall.entity.AnalysisJob;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface AnalysisJobRepository extends JpaRepository<AnalysisJob, UUID> {

    Optional<AnalysisJob> findByIdempotencyKey(String idempotencyKey);

    Page<AnalysisJob> findByStatusOrderByCreatedAtDesc(AnalysisJob.Status status, Pageable pageable);
}
