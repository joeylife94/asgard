package com.heimdall.ratelimit;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import java.time.Duration;

/**
 * Rate Limit Interceptor
 * Intercepts requests and enforces rate limits based on @RateLimit annotation
 */
@Component
public class RateLimitInterceptor implements HandlerInterceptor {
    
    private static final Logger logger = LoggerFactory.getLogger(RateLimitInterceptor.class);
    private static final String RATE_LIMIT_EXCEEDED_MESSAGE = "Rate limit exceeded. Please try again later.";
    
    private final RateLimiterService rateLimiterService;
    
    public RateLimitInterceptor(RateLimiterService rateLimiterService) {
        this.rateLimiterService = rateLimiterService;
    }
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) 
            throws Exception {
        
        if (!(handler instanceof HandlerMethod handlerMethod)) {
            return true;
        }
        
        // Check if method has @RateLimit annotation
        RateLimit rateLimit = handlerMethod.getMethodAnnotation(RateLimit.class);
        if (rateLimit == null) {
            return true;
        }
        
        // Build rate limit key based on key type
        String key = buildRateLimitKey(request, rateLimit.keyType());
        
        // Convert duration to Duration object
        Duration duration = Duration.of(rateLimit.duration(), rateLimit.timeUnit());
        
        // Check rate limit
        boolean allowed = rateLimiterService.isAllowed(key, rateLimit.maxRequests(), duration);
        
        if (!allowed) {
            // Rate limit exceeded
            logger.warn("Rate limit exceeded for key: {}", key);
            
            response.setStatus(429); // 429 Too Many Requests
            response.setContentType("application/json");
            response.getWriter().write(String.format(
                    "{\"error\":\"Too Many Requests\",\"message\":\"%s\",\"retryAfter\":%d}",
                    RATE_LIMIT_EXCEEDED_MESSAGE,
                    rateLimiterService.getTimeUntilReset(key)
            ));
            
            // Add rate limit headers
            addRateLimitHeaders(response, key, rateLimit.maxRequests());
            
            return false;
        }
        
        // Add rate limit headers for successful requests
        addRateLimitHeaders(response, key, rateLimit.maxRequests());
        
        return true;
    }
    
    /**
     * Build rate limit key based on key type
     */
    private String buildRateLimitKey(HttpServletRequest request, RateLimit.KeyType keyType) {
        String endpoint = request.getRequestURI();
        
        return switch (keyType) {
            case USER -> {
                Authentication auth = SecurityContextHolder.getContext().getAuthentication();
                String username = auth != null ? auth.getName() : "anonymous";
                yield String.format("user:%s:%s", username, endpoint);
            }
            case IP -> {
                String ipAddress = getClientIpAddress(request);
                yield String.format("ip:%s:%s", ipAddress, endpoint);
            }
            case API_KEY -> {
                String apiKey = request.getHeader("X-API-Key");
                apiKey = apiKey != null ? apiKey : "no-key";
                yield String.format("apikey:%s:%s", apiKey, endpoint);
            }
        };
    }
    
    /**
     * Get client IP address from request
     */
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        
        String xRealIp = request.getHeader("X-Real-IP");
        if (xRealIp != null && !xRealIp.isEmpty()) {
            return xRealIp;
        }
        
        return request.getRemoteAddr();
    }
    
    /**
     * Add rate limit headers to response
     */
    private void addRateLimitHeaders(HttpServletResponse response, String key, int maxRequests) {
        long remaining = rateLimiterService.getRemainingRequests(key, maxRequests);
        long resetTime = rateLimiterService.getTimeUntilReset(key);
        
        response.addHeader("X-RateLimit-Limit", String.valueOf(maxRequests));
        response.addHeader("X-RateLimit-Remaining", String.valueOf(remaining));
        response.addHeader("X-RateLimit-Reset", String.valueOf(resetTime));
    }
}
