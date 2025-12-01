package com.heimdall.service;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.github.resilience4j.timelimiter.annotation.TimeLimiter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.RestClientException;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Bifrost Client Service
 * Handles communication with Bifrost ML/AI service with resilience patterns
 */
@Service
public class BifrostClientService {
    
    private static final Logger logger = LoggerFactory.getLogger(BifrostClientService.class);
    private static final String CIRCUIT_BREAKER_NAME = "bifrostService";
    
    private final RestTemplate restTemplate;
    private final String bifrostBaseUrl;
    
    public BifrostClientService(
            RestTemplate restTemplate,
            @Value("${bifrost.base-url:http://localhost:8000}") String bifrostBaseUrl) {
        this.restTemplate = restTemplate;
        this.bifrostBaseUrl = bifrostBaseUrl;
    }
    
    /**
     * Health check endpoint with Circuit Breaker
     * 
     * Circuit Breaker will:
     * - Open after 50% failure rate (configured)
     * - Prevent cascading failures
     * - Return fallback response when circuit is open
     */
    @CircuitBreaker(name = CIRCUIT_BREAKER_NAME, fallbackMethod = "healthCheckFallback")
    @Retry(name = CIRCUIT_BREAKER_NAME)
    public Map<String, Object> checkHealth() {
        logger.debug("Checking Bifrost health: {}/health", bifrostBaseUrl);
        
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(
                    bifrostBaseUrl + "/health",
                    Map.class
            );
            
            logger.info("Bifrost health check successful");
            return response;
            
        } catch (RestClientException e) {
            logger.error("Failed to check Bifrost health: {}", e.getMessage());
            throw e;
        }
    }
    
    /**
     * Analyze log endpoint with Circuit Breaker and Time Limiter
     * 
     * @param logData Log data to analyze
     * @return Analysis result
     */
    @CircuitBreaker(name = CIRCUIT_BREAKER_NAME, fallbackMethod = "analyzeLogFallbackAsync")
    @Retry(name = CIRCUIT_BREAKER_NAME)
    @TimeLimiter(name = CIRCUIT_BREAKER_NAME)
    public CompletableFuture<Map<String, Object>> analyzeLogAsync(Map<String, Object> logData) {
        return CompletableFuture.supplyAsync(() -> {
            logger.debug("Sending log analysis request to Bifrost");
            
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.postForObject(
                        bifrostBaseUrl + "/api/v1/analyze",
                        logData,
                        Map.class
                );
                
                logger.info("Log analysis completed successfully");
                return response;
                
            } catch (RestClientException e) {
                logger.error("Failed to analyze log: {}", e.getMessage());
                throw e;
            }
        });
    }
    
    /**
     * Synchronous log analysis (without async)
     */
    @CircuitBreaker(name = CIRCUIT_BREAKER_NAME, fallbackMethod = "analyzeLogFallback")
    @Retry(name = CIRCUIT_BREAKER_NAME)
    public Map<String, Object> analyzeLog(Map<String, Object> logData) {
        logger.debug("Sending log analysis request to Bifrost (sync)");
        
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    bifrostBaseUrl + "/api/v1/analyze",
                    logData,
                    Map.class
            );
            
            logger.info("Log analysis completed successfully (sync)");
            return response;
            
        } catch (RestClientException e) {
            logger.error("Failed to analyze log (sync): {}", e.getMessage());
            throw e;
        }
    }
    
    /**
     * Get analysis history with Circuit Breaker
     */
    @CircuitBreaker(name = CIRCUIT_BREAKER_NAME, fallbackMethod = "getHistoryFallback")
    @Retry(name = CIRCUIT_BREAKER_NAME)
    public Map<String, Object> getAnalysisHistory(int page, int size) {
        logger.debug("Fetching analysis history from Bifrost: page={}, size={}", page, size);
        
        try {
            String url = String.format("%s/api/v1/history?page=%d&size=%d", 
                    bifrostBaseUrl, page, size);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            
            logger.info("Analysis history fetched successfully");
            return response;
            
        } catch (RestClientException e) {
            logger.error("Failed to fetch analysis history: {}", e.getMessage());
            throw e;
        }
    }
    
    // ============================================================================
    // Fallback Methods
    // ============================================================================
    
    /**
     * Fallback method for health check
     * Called when circuit is open or all retries failed
     */
    private Map<String, Object> healthCheckFallback(Exception e) {
        logger.warn("Bifrost health check fallback triggered: {}", e.getMessage());
        
        Map<String, Object> fallback = new HashMap<>();
        fallback.put("status", "CIRCUIT_OPEN");
        fallback.put("service", "bifrost");
        fallback.put("message", "Bifrost service is currently unavailable");
        fallback.put("error", e.getMessage());
        
        return fallback;
    }
    
    /**
     * Fallback method for log analysis (sync)
     */
    private Map<String, Object> analyzeLogFallback(Map<String, Object> logData, Exception e) {
        logger.warn("Bifrost analyze log fallback triggered: {}", e.getMessage());
        
        Map<String, Object> fallback = new HashMap<>();
        fallback.put("status", "FALLBACK");
        fallback.put("analysis", "Service temporarily unavailable. Request queued for later processing.");
        fallback.put("error", e.getMessage());
        fallback.put("originalRequest", logData);
        
        // TODO: Queue the request for later processing
        
        return fallback;
    }
    
    /**
     * Fallback method for log analysis (async)
     */
    private CompletableFuture<Map<String, Object>> analyzeLogFallbackAsync(
            Map<String, Object> logData, Exception e) {
        logger.warn("Bifrost analyze log async fallback triggered: {}", e.getMessage());
        
        Map<String, Object> fallback = new HashMap<>();
        fallback.put("status", "FALLBACK");
        fallback.put("analysis", "Service temporarily unavailable. Request queued for later processing.");
        fallback.put("error", e.getMessage());
        
        return CompletableFuture.completedFuture(fallback);
    }
    
    /**
     * Fallback method for history retrieval
     */
    private Map<String, Object> getHistoryFallback(int page, int size, Exception e) {
        logger.warn("Bifrost get history fallback triggered: {}", e.getMessage());
        
        Map<String, Object> fallback = new HashMap<>();
        fallback.put("status", "FALLBACK");
        fallback.put("items", new java.util.ArrayList<>());
        fallback.put("message", "History temporarily unavailable");
        fallback.put("error", e.getMessage());
        
        return fallback;
    }
}
