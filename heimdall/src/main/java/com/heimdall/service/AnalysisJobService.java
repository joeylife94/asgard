package com.heimdall.service;

import com.heimdall.entity.AnalysisJob;
import com.heimdall.repository.AnalysisJobRepository;
import com.heimdall.util.DateTimeUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnalysisJobService {

    private final AnalysisJobRepository analysisJobRepository;

    @Value("${heimdall.analysis.max-attempts:3}")
    private int maxAttempts;

    @Transactional
    public AnalysisJob createOrGetJob(String idempotencyKey, Long logId, String traceId, Map<String, Object> modelPolicy) {
        Optional<AnalysisJob> existing = analysisJobRepository.findByIdempotencyKey(idempotencyKey);
        if (existing.isPresent()) {
            return existing.get();
        }

        AnalysisJob job = new AnalysisJob();
        job.setJobId(UUID.randomUUID());
        job.setIdempotencyKey(idempotencyKey);
        job.setStatus(AnalysisJob.Status.PENDING);
        job.setAttemptCount(0);
        job.setCreatedAt(DateTimeUtil.now());
        job.setTraceId(traceId);
        job.setModelPolicy(modelPolicy);
        job.setLogId(logId);
        job.setInputRef(logId != null ? "log:" + logId : null);

        try {
            return analysisJobRepository.save(job);
        } catch (DataIntegrityViolationException e) {
            // Concurrent create with same idempotency key
            return analysisJobRepository.findByIdempotencyKey(idempotencyKey)
                .orElseThrow(() -> e);
        }
    }

    @Transactional
    public void markRunning(UUID jobId) {
        AnalysisJob job = analysisJobRepository.findById(jobId)
            .orElseThrow(() -> new IllegalArgumentException("Job not found: " + jobId));

        if (job.getStatus() == AnalysisJob.Status.SUCCEEDED || job.getStatus() == AnalysisJob.Status.FAILED) {
            return;
        }

        job.setStatus(AnalysisJob.Status.RUNNING);
        if (job.getStartedAt() == null) {
            job.setStartedAt(DateTimeUtil.now());
        }
        analysisJobRepository.save(job);
    }

    @Transactional
    public void markSucceeded(UUID jobId, Long resultRef, String resultSummary, Map<String, Object> resultPayload, String traceId) {
        AnalysisJob job = analysisJobRepository.findById(jobId)
            .orElseThrow(() -> new IllegalArgumentException("Job not found: " + jobId));

        // Idempotent completion
        if (job.getStatus() == AnalysisJob.Status.SUCCEEDED) {
            return;
        }

        job.setStatus(AnalysisJob.Status.SUCCEEDED);
        job.setFinishedAt(DateTimeUtil.now());
        job.setResultRef(resultRef);
        job.setResultSummary(resultSummary);
        job.setResultPayload(resultPayload);
        job.setErrorCode(null);
        job.setErrorMessage(null);
        if (traceId != null) {
            job.setTraceId(traceId);
        }

        analysisJobRepository.save(job);
    }

    @Transactional
    public void markFailed(UUID jobId, String errorCode, String errorMessage, String traceId) {
        AnalysisJob job = analysisJobRepository.findById(jobId)
            .orElseThrow(() -> new IllegalArgumentException("Job not found: " + jobId));

        // Do not downgrade a successful job
        if (job.getStatus() == AnalysisJob.Status.SUCCEEDED) {
            return;
        }

        job.setStatus(AnalysisJob.Status.FAILED);
        job.setFinishedAt(DateTimeUtil.now());
        job.setErrorCode(errorCode);
        job.setErrorMessage(errorMessage);
        if (traceId != null) {
            job.setTraceId(traceId);
        }

        analysisJobRepository.save(job);
    }

    @Transactional
    public boolean canRetry(AnalysisJob job) {
        return job.getAttemptCount() < maxAttempts;
    }

    @Transactional
    public AnalysisJob prepareRetry(UUID jobId) {
        AnalysisJob job = analysisJobRepository.findById(jobId)
            .orElseThrow(() -> new IllegalArgumentException("Job not found: " + jobId));

        if (job.getStatus() != AnalysisJob.Status.FAILED) {
            return job;
        }

        if (!canRetry(job)) {
            return job;
        }

        job.setAttemptCount(job.getAttemptCount() + 1);
        job.setStatus(AnalysisJob.Status.PENDING);
        job.setStartedAt(null);
        job.setFinishedAt(null);
        job.setErrorCode(null);
        job.setErrorMessage(null);

        return analysisJobRepository.save(job);
    }

    @Transactional(readOnly = true)
    public AnalysisJob get(UUID jobId) {
        return analysisJobRepository.findById(jobId)
            .orElseThrow(() -> new IllegalArgumentException("Job not found: " + jobId));
    }

    @Transactional(readOnly = true)
    public Optional<AnalysisJob> findById(UUID jobId) {
        return analysisJobRepository.findById(jobId);
    }

    @Transactional(readOnly = true)
    public Optional<AnalysisJob> findByIdempotencyKey(String idempotencyKey) {
        return analysisJobRepository.findByIdempotencyKey(idempotencyKey);
    }

    @Transactional(readOnly = true)
    public Page<AnalysisJob> listFailed(Pageable pageable) {
        return analysisJobRepository.findByStatusOrderByCreatedAtDesc(AnalysisJob.Status.FAILED, pageable);
    }
}
