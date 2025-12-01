package com.heimdall.ratelimit;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for RateLimiterService
 */
@ExtendWith(MockitoExtension.class)
class RateLimiterServiceTest {
    
    @Mock
    private RedisTemplate<String, Long> redisTemplate;
    
    @Mock
    private ValueOperations<String, Long> valueOperations;
    
    private RateLimiterService rateLimiterService;
    
    @BeforeEach
    void setUp() {
        lenient().when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        rateLimiterService = new RateLimiterService(redisTemplate);
    }
    
    // ============================================================================
    // isAllowed Tests
    // ============================================================================
    
    @Test
    void isAllowed_FirstRequest_ShouldAllow() {
        // Given
        String key = "user:123:api";
        int maxRequests = 100;
        Duration duration = Duration.ofHours(1);
        
        when(valueOperations.get("ratelimit:" + key)).thenReturn(null);
        
        // When
        boolean allowed = rateLimiterService.isAllowed(key, maxRequests, duration);
        
        // Then
        assertThat(allowed).isTrue();
        verify(valueOperations).set(eq("ratelimit:" + key), eq(1L), eq(3600L), eq(TimeUnit.SECONDS));
    }
    
    @Test
    void isAllowed_WithinLimit_ShouldAllow() {
        // Given
        String key = "user:123:api";
        int maxRequests = 100;
        Duration duration = Duration.ofHours(1);
        
        when(valueOperations.get("ratelimit:" + key)).thenReturn(50L);
        
        // When
        boolean allowed = rateLimiterService.isAllowed(key, maxRequests, duration);
        
        // Then
        assertThat(allowed).isTrue();
        verify(valueOperations).increment("ratelimit:" + key);
    }
    
    @Test
    void isAllowed_ExceedsLimit_ShouldDeny() {
        // Given
        String key = "user:123:api";
        int maxRequests = 100;
        Duration duration = Duration.ofHours(1);
        
        when(valueOperations.get("ratelimit:" + key)).thenReturn(100L);
        
        // When
        boolean allowed = rateLimiterService.isAllowed(key, maxRequests, duration);
        
        // Then
        assertThat(allowed).isFalse();
        verify(valueOperations, never()).increment(anyString());
    }
    
    @Test
    void isAllowed_AtLimit_ShouldDeny() {
        // Given
        String key = "user:123:api";
        int maxRequests = 100;
        Duration duration = Duration.ofHours(1);
        
        when(valueOperations.get("ratelimit:" + key)).thenReturn(101L);
        
        // When
        boolean allowed = rateLimiterService.isAllowed(key, maxRequests, duration);
        
        // Then
        assertThat(allowed).isFalse();
    }
    
    // ============================================================================
    // getRemainingRequests Tests
    // ============================================================================
    
    @Test
    void getRemainingRequests_NoRequests_ShouldReturnMax() {
        // Given
        String key = "user:123:api";
        int maxRequests = 100;
        
        when(valueOperations.get("ratelimit:" + key)).thenReturn(null);
        
        // When
        long remaining = rateLimiterService.getRemainingRequests(key, maxRequests);
        
        // Then
        assertThat(remaining).isEqualTo(100);
    }
    
    @Test
    void getRemainingRequests_WithRequests_ShouldReturnRemaining() {
        // Given
        String key = "user:123:api";
        int maxRequests = 100;
        
        when(valueOperations.get("ratelimit:" + key)).thenReturn(30L);
        
        // When
        long remaining = rateLimiterService.getRemainingRequests(key, maxRequests);
        
        // Then
        assertThat(remaining).isEqualTo(70);
    }
    
    @Test
    void getRemainingRequests_ExceedsLimit_ShouldReturnZero() {
        // Given
        String key = "user:123:api";
        int maxRequests = 100;
        
        when(valueOperations.get("ratelimit:" + key)).thenReturn(150L);
        
        // When
        long remaining = rateLimiterService.getRemainingRequests(key, maxRequests);
        
        // Then
        assertThat(remaining).isEqualTo(0);
    }
    
    // ============================================================================
    // getTimeUntilReset Tests
    // ============================================================================
    
    @Test
    void getTimeUntilReset_WithTTL_ShouldReturnSeconds() {
        // Given
        String key = "user:123:api";
        
        when(redisTemplate.getExpire("ratelimit:" + key, TimeUnit.SECONDS)).thenReturn(1800L);
        
        // When
        long ttl = rateLimiterService.getTimeUntilReset(key);
        
        // Then
        assertThat(ttl).isEqualTo(1800);
    }
    
    @Test
    void getTimeUntilReset_NoTTL_ShouldReturnZero() {
        // Given
        String key = "user:123:api";
        
        when(redisTemplate.getExpire("ratelimit:" + key, TimeUnit.SECONDS)).thenReturn(-1L);
        
        // When
        long ttl = rateLimiterService.getTimeUntilReset(key);
        
        // Then
        assertThat(ttl).isEqualTo(0);
    }
    
    @Test
    void getTimeUntilReset_NullTTL_ShouldReturnZero() {
        // Given
        String key = "user:123:api";
        
        when(redisTemplate.getExpire("ratelimit:" + key, TimeUnit.SECONDS)).thenReturn(null);
        
        // When
        long ttl = rateLimiterService.getTimeUntilReset(key);
        
        // Then
        assertThat(ttl).isEqualTo(0);
    }
    
    // ============================================================================
    // resetLimit Tests
    // ============================================================================
    
    @Test
    void resetLimit_ShouldDeleteKey() {
        // Given
        String key = "user:123:api";
        
        // When
        rateLimiterService.resetLimit(key);
        
        // Then
        verify(redisTemplate).delete("ratelimit:" + key);
    }
}
