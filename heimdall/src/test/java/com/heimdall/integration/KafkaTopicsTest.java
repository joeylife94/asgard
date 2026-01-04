package com.heimdall.integration;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.test.context.EmbeddedKafka;
import org.springframework.test.context.ActiveProfiles;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@ActiveProfiles("test")
@EmbeddedKafka(partitions = 1)
@DisplayName("Kafka E2E Skeleton Tests")
class KafkaTopicsTest {

    @Autowired(required = false)
    private KafkaAdmin kafkaAdmin;

    @Test
    @DisplayName("Spring context should load with EmbeddedKafka")
    void contextLoadsWithEmbeddedKafka() {
        // This is a skeleton test to ensure the wiring for EmbeddedKafka works.
        // Follow-up: add produce/consume round-trip tests for analysis.request/result topics.
        assertThat(true).isTrue();
    }
}
