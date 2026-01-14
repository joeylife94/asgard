package com.heimdall.kafka.listener;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.heimdall.entity.AnalysisJob;
import com.heimdall.kafka.event.DlqFailedEvent;
import com.heimdall.repository.AnalysisJobRepository;
import com.heimdall.service.AnalysisJobService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
@Slf4j
public class DlqFailedListener {

    private final ObjectMapper objectMapper;
    private final AnalysisJobRepository analysisJobRepository;
    private final AnalysisJobService analysisJobService;

    @KafkaListener(
        topics = "${kafka.topics.dlq-failed}",
        groupId = "${spring.kafka.consumer.group-id}",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void handleDlqFailed(
        @Payload String message,
        @Header(KafkaHeaders.RECEIVED_KEY) String key,
        @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
        @Header(KafkaHeaders.OFFSET) long offset,
        Acknowledgment acknowledgment
    ) {
        try {
            DlqFailedEvent event = objectMapper.readValue(message, DlqFailedEvent.class);

            Optional<AnalysisJob> jobOpt = Optional.empty();
            UUID jobId = event.getJobId();
            if (jobId != null) {
                jobOpt = analysisJobRepository.findById(jobId);
            }
            if (jobOpt.isEmpty() && event.getIdempotencyKey() != null) {
                jobOpt = analysisJobRepository.findByIdempotencyKey(event.getIdempotencyKey());
            }

            if (jobOpt.isPresent()) {
                AnalysisJob job = jobOpt.get();
                analysisJobService.markFailed(
                    job.getJobId(),
                    event.getErrorCode() != null ? event.getErrorCode() : "DLQ_FAILED",
                    event.getErrorMessage(),
                    event.getTraceId()
                );
                log.warn(
                    "DLQ failed event applied: jobId={}, key={}, partition={}, offset={}",
                    job.getJobId(), key, partition, offset
                );
            } else {
                log.warn(
                    "DLQ failed event received but job not found: key={}, partition={}, offset={}",
                    key, partition, offset
                );
            }

            acknowledgment.acknowledge();
        } catch (Exception e) {
            log.error(
                "Error processing dlq.failed message: key={}, partition={}, offset={}",
                key, partition, offset, e
            );
            // Let the container error handler retry and eventually publish to DLT.
            throw new RuntimeException(e);
        }
    }
}
