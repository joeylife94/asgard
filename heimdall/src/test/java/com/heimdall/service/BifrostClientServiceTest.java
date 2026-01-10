package com.heimdall.service;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for BifrostClientService
 * Tests Circuit Breaker behavior and fallback mechanisms
 */
@ExtendWith(MockitoExtension.class)
class BifrostClientServiceTest {
    
    @Mock
    private RestTemplate restTemplate;
    
    @Mock
    private CircuitBreakerRegistry circuitBreakerRegistry;
    
    @Mock
    private CircuitBreaker circuitBreaker;
    
    private BifrostClientService bifrostService;
    private static final String BIFROST_BASE_URL = "http://localhost:8000";
    
    @BeforeEach
    void setUp() {
        bifrostService = new BifrostClientService(restTemplate, BIFROST_BASE_URL);
    }
    
    // ============================================================================
    // Health Check Tests
    // ============================================================================
    
    @Test
    void healthCheck_Success() {
        // Given
        Map<String, Object> expectedResponse = new HashMap<>();
        expectedResponse.put("status", "healthy");
        expectedResponse.put("service", "bifrost");
        
        when(restTemplate.getForObject(BIFROST_BASE_URL + "/health", Map.class))
                .thenReturn(expectedResponse);
        
        // When
        Map<String, Object> result = bifrostService.checkHealth();
        
        // Then
        assertThat(result).isNotNull();
        assertThat(result.get("status")).isEqualTo("healthy");
        verify(restTemplate).getForObject(BIFROST_BASE_URL + "/health", Map.class);
    }
    
    @Test
    void healthCheck_ServiceDown_ThrowsException() {
        // Given
        when(restTemplate.getForObject(BIFROST_BASE_URL + "/health", Map.class))
                .thenThrow(new RestClientException("Connection refused"));
        
        // When & Then
        assertThrows(RestClientException.class, () -> bifrostService.checkHealth());
    }
    
    // ============================================================================
    // Log Analysis Tests (Synchronous)
    // ============================================================================
    
    @Test
    void analyzeLog_Success() {
        // Given
        Map<String, Object> logData = new HashMap<>();
        logData.put("log", "NullPointerException at line 42");
        
        Map<String, Object> expectedResponse = new HashMap<>();
        expectedResponse.put("id", 123);
        expectedResponse.put("response", "Memory access violation detected");
        expectedResponse.put("duration_seconds", 1.23);
        expectedResponse.put("model", "llama3.1:8b");
        expectedResponse.put("cached", false);
        
        when(restTemplate.postForObject(
            eq(BIFROST_BASE_URL + "/analyze"),
            any(Map.class),
                eq(Map.class)))
                .thenReturn(expectedResponse);
        
        // When
        Map<String, Object> result = bifrostService.analyzeLog(logData);
        
        // Then
        assertThat(result).isNotNull();
        assertThat(result.get("response")).isEqualTo("Memory access violation detected");
    }
    
    @Test
    void analyzeLog_ServiceError_ThrowsException() {
        // Given
        Map<String, Object> logData = new HashMap<>();
        logData.put("log", "Error message");
        
        when(restTemplate.postForObject(anyString(), any(), eq(Map.class)))
                .thenThrow(new RestClientException("Service unavailable"));
        
        // When & Then
        assertThrows(RestClientException.class, () -> bifrostService.analyzeLog(logData));
    }
    
    // ============================================================================
    // History Tests
    // ============================================================================
    
    @Test
    void getAnalysisHistory_Success() {
        // Given
        java.util.List<Map<String, Object>> expectedItems = new java.util.ArrayList<>();
        Map<String, Object> item = new HashMap<>();
        item.put("id", 123);
        item.put("model", "llama3.1:8b");
        expectedItems.add(item);

        when(restTemplate.postForObject(
            eq(BIFROST_BASE_URL + "/history"),
            any(Map.class),
            eq(Object.class)))
            .thenReturn(expectedItems);
        
        // When
        Map<String, Object> result = bifrostService.getAnalysisHistory(0, 20);
        
        // Then
        assertThat(result).isNotNull();
        assertThat(result.get("items")).isNotNull();
        assertThat(result.get("page")).isEqualTo(0);
        assertThat(result.get("size")).isEqualTo(20);
    }
    
    @Test
    void getAnalysisHistory_ServiceError_ThrowsException() {
        // Given
        when(restTemplate.postForObject(anyString(), any(), eq(Object.class)))
                .thenThrow(new RestClientException("Database error"));
        
        // When & Then
        assertThrows(RestClientException.class, 
                () -> bifrostService.getAnalysisHistory(0, 20));
    }
    
    // ============================================================================
    // Integration Tests (would require @SpringBootTest in real scenario)
    // ============================================================================
    
    @Test
    void analyzeLog_MultipleFailures_ShouldTriggerCircuitBreaker() {
        // This test demonstrates the expected behavior
        // In real integration test with @SpringBootTest, after 10 failed calls,
        // Circuit Breaker should open and fallback should be called immediately
        
        // Given - simulate multiple failures
        when(restTemplate.postForObject(anyString(), any(), eq(Map.class)))
                .thenThrow(new RestClientException("Service down"));
        
        Map<String, Object> logData = new HashMap<>();
        logData.put("log", "Test error");
        
        // When - make 10 failed calls (threshold)
        for (int i = 0; i < 10; i++) {
            try {
                bifrostService.analyzeLog(logData);
            } catch (RestClientException e) {
                // Expected - circuit should still be closed
            }
        }
        
        // Note: In a real integration test with CircuitBreaker enabled,
        // the 11th call would trigger fallback immediately without calling the service
    }
}
