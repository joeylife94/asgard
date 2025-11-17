package com.heimdall;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@SpringBootApplication
public class HeimdallApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(HeimdallApplication.class, args);
    }
    
    @Configuration
    @EnableJpaRepositories
    @EnableTransactionManagement
    @ConditionalOnProperty(name = "spring.jpa.enabled", havingValue = "true", matchIfMissing = false)
    static class JpaConfiguration {
    }
    
    @Configuration
    @EnableKafka
    @ConditionalOnProperty(name = "spring.kafka.enabled", havingValue = "true", matchIfMissing = false)
    static class KafkaConfiguration {
    }
    
    @Configuration
    @EnableAsync
    @ConditionalOnProperty(name = "spring.async.enabled", havingValue = "true", matchIfMissing = true)
    static class AsyncConfiguration {
    }
}
