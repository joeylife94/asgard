package com.heimdall.ratelimit;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.time.temporal.ChronoUnit;

/**
 * Rate Limit Annotation
 * Apply to controller methods to enforce rate limiting
 * 
 * Usage:
 * @RateLimit(maxRequests = 100, duration = 1, timeUnit = ChronoUnit.HOURS)
 * public ResponseEntity<?> myEndpoint() { ... }
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RateLimit {
    
    /**
     * Maximum number of requests allowed within the time window
     */
    int maxRequests() default 100;
    
    /**
     * Duration of the time window
     */
    long duration() default 1;
    
    /**
     * Time unit for the duration
     */
    ChronoUnit timeUnit() default ChronoUnit.HOURS;
    
    /**
     * Key type for rate limiting
     * USER: Limit per user (based on authentication)
     * IP: Limit per IP address
     * API_KEY: Limit per API key
     */
    KeyType keyType() default KeyType.USER;
    
    enum KeyType {
        USER,
        IP,
        API_KEY
    }
}
