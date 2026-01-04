package com.heimdall.ratelimit;

import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.RedisConnectionFailureException;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

/**
 * Redis-based Rate Limiter Service
 * Implements token bucket algorithm using Redis
 */
@Service
public class RateLimiterService {
    
    private final RedisTemplate<String, Long> redisTemplate;
    
    public RateLimiterService(RedisTemplate<String, Long> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }
    
    /**
     * Check if request is allowed based on rate limit
     * 
     * @param key Unique key for rate limiting (e.g., "user:123:api")
     * @param maxRequests Maximum number of requests allowed
     * @param duration Time window duration
     * @return true if request is allowed, false if rate limit exceeded
     */
    public boolean isAllowed(String key, int maxRequests, Duration duration) {
        String redisKey = "ratelimit:" + key;

        try {
            // Get current counter
            Long currentCount = redisTemplate.opsForValue().get(redisKey);

            if (currentCount == null) {
                // First request - initialize counter
                redisTemplate.opsForValue().set(redisKey, 1L, duration.getSeconds(), TimeUnit.SECONDS);
                return true;
            }

            if (currentCount >= maxRequests) {
                // Rate limit exceeded
                return false;
            }

            // Increment counter
            redisTemplate.opsForValue().increment(redisKey);
            return true;
        } catch (RedisConnectionFailureException ex) {
            // Fail-open when Redis is unavailable to avoid taking down core APIs.
            return true;
        }
    }
    
    /**
     * Get remaining requests for a key
     * 
     * @param key Rate limit key
     * @param maxRequests Maximum requests allowed
     * @return Number of remaining requests
     */
    public long getRemainingRequests(String key, int maxRequests) {
        String redisKey = "ratelimit:" + key;

        try {
            Long currentCount = redisTemplate.opsForValue().get(redisKey);

            if (currentCount == null) {
                return maxRequests;
            }

            return Math.max(0, maxRequests - currentCount);
        } catch (RedisConnectionFailureException ex) {
            return maxRequests;
        }
    }
    
    /**
     * Get time until rate limit reset
     * 
     * @param key Rate limit key
     * @return Seconds until reset, or 0 if no limit active
     */
    public long getTimeUntilReset(String key) {
        String redisKey = "ratelimit:" + key;

        try {
            Long ttl = redisTemplate.getExpire(redisKey, TimeUnit.SECONDS);
            return ttl != null && ttl > 0 ? ttl : 0;
        } catch (RedisConnectionFailureException ex) {
            return 0;
        }
    }
    
    /**
     * Reset rate limit for a key (admin function)
     * 
     * @param key Rate limit key
     */
    public void resetLimit(String key) {
        String redisKey = "ratelimit:" + key;
        redisTemplate.delete(redisKey);
    }
}
