package com.heimdall.service;

import com.heimdall.entity.AnalysisJob;
import com.heimdall.entity.AnalysisResult;
import com.heimdall.entity.LogEntry;
import com.heimdall.kafka.event.AnalysisResultEvent;
import com.heimdall.repository.AnalysisResultRepository;
import com.heimdall.repository.LogEntryRepository;
import com.heimdall.util.DateTimeUtil;
import io.micrometer.core.instrument.MeterRegistry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class LogProcessingService {
    
    private final LogEntryRepository logEntryRepository;
    private final AnalysisResultRepository analysisResultRepository;
    private final AnalysisJobService analysisJobService;
    private final NotificationService notificationService;
    private final MeterRegistry meterRegistry;
    
    /**
     * Process analysis result with idempotency protection.
     * Handles at-least-once delivery by checking job status before processing.
     */
    @Transactional
    public void processAnalysisResult(AnalysisResultEvent event) {
        log.info("Processing analysis result: jobId={}, logId={}, status={}",
            event.getJobId(), event.getLogId(), event.getStatus());

        UUID jobId = event.getJobId();
        if (jobId == null) {
            throw new IllegalArgumentException("Missing job_id in analysis result event");
        }

        if (event.getStatus() == null) {
            throw new IllegalArgumentException("Missing status in analysis result event");
        }

        // ====== IDEMPOTENCY CHECK ======
        // Check if this result has already been processed (duplicate message)
        Optional<AnalysisJob> existingJob = analysisJobService.findById(jobId);
        if (existingJob.isPresent()) {
            AnalysisJob job = existingJob.get();
            
            // If job is already in terminal state, this is a duplicate message
            if (job.getStatus() == AnalysisJob.Status.SUCCEEDED) {
                log.warn("Duplicate result received for already succeeded job: jobId={}, ignoring", jobId);
                meterRegistry.counter("ai_job_duplicate_result_total", "status", "succeeded").increment();
                return;
            }
            
            // For failed jobs receiving success result, allow processing (retry scenario)
            // But if failed job receives another failed result, skip
            if (job.getStatus() == AnalysisJob.Status.FAILED && "FAILED".equalsIgnoreCase(event.getStatus())) {
                log.warn("Duplicate failed result for already failed job: jobId={}, ignoring", jobId);
                meterRegistry.counter("ai_job_duplicate_result_total", "status", "failed").increment();
                return;
            }
        }
        // ====== END IDEMPOTENCY CHECK ======

        if ("FAILED".equalsIgnoreCase(event.getStatus())) {
            analysisJobService.markFailed(jobId, event.getErrorCode(), event.getErrorMessage(), event.getTraceId());
            meterRegistry.counter("ai_job_failed_total").increment();
            return;
        }
        
        // Check if analysis result already exists for this request (another layer of idempotency)
        Optional<AnalysisResult> existingResult = analysisResultRepository.findByRequestId(jobId.toString());
        if (existingResult.isPresent()) {
            log.warn("Duplicate result: analysis result already exists for jobId={}, resultId={}", 
                jobId, existingResult.get().getId());
            meterRegistry.counter("ai_job_duplicate_result_total", "status", "result_exists").increment();
            
            // Still mark job as succeeded if not already
            analysisJobService.markSucceeded(
                jobId,
                existingResult.get().getId(),
                existingResult.get().getSummary(),
                null,
                event.getTraceId()
            );
            return;
        }
        
        // 로그 엔트리 조회
        LogEntry logEntry = logEntryRepository.findById(event.getLogId())
            .orElseThrow(() -> new RuntimeException("LogEntry not found: " + event.getLogId()));
        
        // 분석 결과 생성
        AnalysisResult analysisResult = new AnalysisResult();
        analysisResult.setLogEntry(logEntry);
        analysisResult.setRequestId(jobId.toString());
        analysisResult.setCorrelationId(event.getTraceId());
        analysisResult.setSummary(event.getSummary());
        analysisResult.setRootCause(event.getRootCause());
        analysisResult.setRecommendation(event.getRecommendation());
        analysisResult.setSeverity(event.getSeverity());
        analysisResult.setConfidence(event.getConfidence());
        analysisResult.setModel(event.getModelUsed());
        if (event.getLatencyMs() != null) {
            analysisResult.setDurationSeconds(new java.math.BigDecimal(event.getLatencyMs()).divide(java.math.BigDecimal.valueOf(1000), 2, java.math.RoundingMode.HALF_UP));
        }
        analysisResult.setAnalyzedAt(event.getTimestamp() != null ? event.getTimestamp() : DateTimeUtil.now());
        analysisResult.setCreatedAt(DateTimeUtil.now());
        
        // 데이터베이스 저장
        AnalysisResult savedResult = analysisResultRepository.save(analysisResult);

        analysisJobService.markSucceeded(
            jobId,
            savedResult.getId(),
            savedResult.getSummary(),
            null,
            event.getTraceId()
        );
        
        // 메트릭 기록
        meterRegistry.counter("ai_job_success_total").increment();
        if (event.getLatencyMs() != null) {
            meterRegistry.timer("ai_job_latency_ms").record(java.time.Duration.ofMillis(event.getLatencyMs()));
        }
        
        // 알림 처리 (조건 충족 시)
        if (shouldSendNotification(savedResult)) {
            notificationService.sendAnalysisNotification(savedResult);
        }
        
        log.info("Analysis result processed: analysisId={}, logId={}, jobId={}",
            savedResult.getId(), logEntry.getId(), jobId);
    }
    
    private boolean shouldSendNotification(AnalysisResult analysisResult) {
        // HIGH 또는 CRITICAL 심각도인 경우 알림 발송
        return "HIGH".equals(analysisResult.getSeverity()) ||
               "CRITICAL".equals(analysisResult.getSeverity());
    }
}
