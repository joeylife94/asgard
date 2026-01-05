package com.heimdall.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.heimdall.entity.AnalysisJob;
import com.heimdall.entity.LogEntry;
import com.heimdall.kafka.event.AnalysisRequestEvent;
import com.heimdall.kafka.producer.KafkaProducerService;
import com.heimdall.repository.LogEntryRepository;
import com.heimdall.util.DateTimeUtil;
import io.micrometer.core.instrument.MeterRegistry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnalysisOrchestratorService {

    private final LogEntryRepository logEntryRepository;
    private final AnalysisJobService analysisJobService;
    private final KafkaProducerService kafkaProducerService;
    private final MeterRegistry meterRegistry;
    private final ObjectMapper objectMapper;

    @Transactional
    public OrchestrationResult requestAnalysisForLog(Long logId, String idempotencyKey, String traceId, JsonNode modelPolicy) {
        LogEntry logEntry = logEntryRepository.findById(logId)
            .orElseThrow(() -> new IllegalArgumentException("LogEntry not found: " + logId));

        Optional<AnalysisJob> existing = analysisJobService.findByIdempotencyKey(idempotencyKey);
        if (existing.isPresent()) {
            return new OrchestrationResult(existing.get(), false);
        }

        AnalysisJob job = analysisJobService.createOrGetJob(
            idempotencyKey,
            logEntry.getId(),
            traceId,
            null
        );

        AnalysisRequestEvent event = AnalysisRequestEvent.builder()
            .schemaVersion(1)
            .jobId(job.getJobId())
            .idempotencyKey(job.getIdempotencyKey())
            .logId(logEntry.getId())
            .traceId(traceId)
            .timestamp(DateTimeUtil.now())
            .priority(logEntry.getSeverity().name())
            .modelPolicy(modelPolicy)
            .build();

        kafkaProducerService.sendAnalysisRequest(event);
        analysisJobService.markRunning(job.getJobId());

        meterRegistry.counter("ai_job_requested_total").increment();
        return new OrchestrationResult(job, true);
    }

    @Transactional
    public OrchestrationResult redriveJob(UUID jobId, String traceId) {
        AnalysisJob job = analysisJobService.prepareRetry(jobId);

        if (job.getStatus() != AnalysisJob.Status.PENDING) {
            return new OrchestrationResult(job, false);
        }

        Long logId = job.getLogId();
        if (logId == null) {
            throw new IllegalStateException("Job has no logId: " + jobId);
        }

        LogEntry logEntry = logEntryRepository.findById(logId)
            .orElseThrow(() -> new IllegalArgumentException("LogEntry not found: " + logId));

        AnalysisRequestEvent event = AnalysisRequestEvent.builder()
            .schemaVersion(1)
            .jobId(job.getJobId())
            .idempotencyKey(job.getIdempotencyKey())
            .logId(logEntry.getId())
            .traceId(traceId != null ? traceId : job.getTraceId())
            .timestamp(DateTimeUtil.now())
            .priority(logEntry.getSeverity() != null ? logEntry.getSeverity().name() : null)
            .modelPolicy(job.getModelPolicy() != null ? objectMapper.valueToTree(job.getModelPolicy()) : null)
            .build();

        kafkaProducerService.sendAnalysisRequest(event);
        analysisJobService.markRunning(job.getJobId());
        meterRegistry.counter("ai_job_redriven_total").increment();

        return new OrchestrationResult(job, true);
    }

    public record OrchestrationResult(AnalysisJob job, boolean created) {}
}

