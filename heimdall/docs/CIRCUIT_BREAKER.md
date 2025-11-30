# Circuit Breaker Pattern Implementation

This document describes the Circuit Breaker pattern implementation in Heimdall using Resilience4j.

## Overview

The Circuit Breaker pattern prevents cascading failures by stopping requests to a failing service, allowing it time to recover. When the circuit is "open," requests fail immediately without attempting to call the failing service.

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Client    │────────▶│  Circuit Breaker │────────▶│   Bifrost   │
│             │         │   (Resilience4j)  │         │   Service   │
└─────────────┘         └──────────────────┘         └─────────────┘
                                │
                                ▼
                        ┌──────────────┐
                        │   Fallback   │
                        │   Response   │
                        └──────────────┘
```

## Configuration

### Circuit Breaker Settings

Located in `Resilience4jConfig.java`:

```yaml
Circuit Breaker: bifrostService
  - Failure Rate Threshold: 50%
  - Minimum Calls: 10
  - Wait Duration (Open): 60 seconds
  - Permitted Calls (Half-Open): 3
  - Sliding Window Size: 100 calls
  - Timeout: 10 seconds
```

### States

1. **CLOSED** (Normal)
   - All requests pass through
   - Monitors failure rate
   - Opens if failure rate exceeds 50%

2. **OPEN** (Service Down)
   - All requests fail immediately
   - Returns fallback response
   - Waits 60 seconds before attempting recovery

3. **HALF_OPEN** (Testing Recovery)
   - Allows 3 test requests
   - Closes if all succeed
   - Opens again if any fail

## Usage

### BifrostClientService

The service is automatically protected with Circuit Breaker annotations:

```java
@Service
public class BifrostClientService {
    
    @CircuitBreaker(name = "bifrostService", fallbackMethod = "healthCheckFallback")
    @Retry(name = "bifrostService")
    public Map<String, Object> checkHealth() {
        // Call to Bifrost service
    }
    
    private Map<String, Object> healthCheckFallback(Exception e) {
        // Fallback response when circuit is open
        return Map.of(
            "status", "CIRCUIT_OPEN",
            "message", "Bifrost service is currently unavailable"
        );
    }
}
```

### API Endpoints

#### 1. Check Bifrost Health

**Endpoint:** `GET /api/bifrost/health`

**Response (Normal):**
```json
{
  "status": "healthy",
  "service": "bifrost",
  "version": "0.2.1"
}
```

**Response (Circuit Open):**
```json
{
  "status": "CIRCUIT_OPEN",
  "service": "bifrost",
  "message": "Bifrost service is currently unavailable",
  "error": "Connection refused"
}
```

#### 2. Analyze Log (Sync)

**Endpoint:** `POST /api/bifrost/analyze`

**Request:**
```json
{
  "log": "NullPointerException at line 42",
  "level": "ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response (Normal):**
```json
{
  "analysis": "Memory access violation detected",
  "severity": "HIGH",
  "recommendations": [
    "Check null pointer handling",
    "Review memory allocation"
  ]
}
```

**Response (Circuit Open):**
```json
{
  "status": "FALLBACK",
  "analysis": "Service temporarily unavailable. Request queued for later processing.",
  "error": "CircuitBreaker 'bifrostService' is OPEN",
  "originalRequest": { ... }
}
```

#### 3. Analyze Log (Async)

**Endpoint:** `POST /api/bifrost/analyze/async`

Returns a `CompletableFuture` with the same response format.

#### 4. Get Analysis History

**Endpoint:** `GET /api/bifrost/history?page=0&size=20`

**Response (Normal):**
```json
{
  "items": [...],
  "total": 100,
  "page": 0,
  "size": 20
}
```

**Response (Circuit Open):**
```json
{
  "status": "FALLBACK",
  "items": [],
  "message": "History temporarily unavailable",
  "error": "CircuitBreaker 'bifrostService' is OPEN"
}
```

## Monitoring

### Actuator Endpoints

Circuit Breaker status is available via Spring Boot Actuator:

**Get Circuit Breaker Status:**
```powershell
curl http://localhost:8080/actuator/circuitbreakers
```

**Response:**
```json
{
  "circuitBreakers": {
    "bifrostService": {
      "state": "CLOSED",
      "failureRate": "25.0%",
      "bufferedCalls": 100,
      "failedCalls": 25,
      "notPermittedCalls": 0
    }
  }
}
```

**Get Circuit Breaker Events:**
```powershell
curl http://localhost:8080/actuator/circuitbreakerevents
```

**Response:**
```json
{
  "circuitBreakerEvents": [
    {
      "circuitBreakerName": "bifrostService",
      "type": "STATE_TRANSITION",
      "creationTime": "2024-01-15T10:30:00Z",
      "stateTransition": "CLOSED_TO_OPEN",
      "elapsedDuration": "PT0S"
    }
  ]
}
```

### Prometheus Metrics

Circuit Breaker metrics are exported to Prometheus:

```
# Circuit breaker state (0=closed, 1=open, 2=half_open)
resilience4j_circuitbreaker_state{name="bifrostService"} 0

# Failure rate percentage
resilience4j_circuitbreaker_failure_rate{name="bifrostService"} 25.0

# Total calls
resilience4j_circuitbreaker_calls_seconds_count{name="bifrostService",kind="successful"} 75
resilience4j_circuitbreaker_calls_seconds_count{name="bifrostService",kind="failed"} 25

# Not permitted calls (when circuit is open)
resilience4j_circuitbreaker_not_permitted_calls_total{name="bifrostService"} 0
```

## Testing

### Unit Tests

Run unit tests for Circuit Breaker:

```powershell
.\gradlew test --tests "BifrostClientServiceTest"
```

### Integration Tests

Test Circuit Breaker behavior with a running system:

1. **Start services:**
   ```powershell
   .\start-all.ps1
   ```

2. **Test normal behavior:**
   ```powershell
   # Should return healthy status
   curl http://localhost:8080/api/bifrost/health
   ```

3. **Simulate service failure:**
   ```powershell
   # Stop Bifrost service
   docker stop bifrost
   
   # Make 10+ requests to trigger circuit breaker
   for ($i=1; $i -le 15; $i++) {
       curl http://localhost:8080/api/bifrost/health
   }
   
   # After 10 failures, circuit should open
   # Subsequent requests should fail immediately with CIRCUIT_OPEN
   ```

4. **Test recovery:**
   ```powershell
   # Restart Bifrost
   docker start bifrost
   
   # Wait 60 seconds (wait duration)
   # Circuit enters HALF_OPEN state
   
   # Make a few requests
   curl http://localhost:8080/api/bifrost/health
   
   # If successful, circuit closes automatically
   ```

## Fallback Strategies

### 1. Default Response

Returns a safe default response indicating service unavailability:

```java
private Map<String, Object> healthCheckFallback(Exception e) {
    return Map.of(
        "status", "CIRCUIT_OPEN",
        "message", "Service temporarily unavailable"
    );
}
```

### 2. Queue for Later Processing

For analysis requests, the fallback can queue the request:

```java
private Map<String, Object> analyzeLogFallback(Map<String, Object> logData, Exception e) {
    // TODO: Queue the request to Kafka for later processing
    kafkaTemplate.send("analysis.deferred", logData);
    
    return Map.of(
        "status", "QUEUED",
        "message", "Request queued for processing when service recovers"
    );
}
```

### 3. Cache Lookup

For history requests, return cached data:

```java
private Map<String, Object> getHistoryFallback(int page, int size, Exception e) {
    // Return cached results if available
    return cacheService.getCachedHistory(page, size)
        .orElse(Map.of("items", List.of(), "message", "Using cached data"));
}
```

## Best Practices

### 1. Configure Appropriate Thresholds

- **Failure Rate:** 50% is a good default, adjust based on your SLA
- **Minimum Calls:** Need enough data to make decisions (10-20 calls)
- **Wait Duration:** Balance between recovery time and user experience (30-60s)

### 2. Implement Meaningful Fallbacks

- Return cached data when possible
- Queue requests for later processing
- Provide clear error messages to users

### 3. Monitor Circuit Breaker Events

- Set up alerts for OPEN state transitions
- Track failure rates and slow calls
- Monitor recovery patterns

### 4. Test Failure Scenarios

- Regularly test circuit breaker behavior
- Use chaos engineering to simulate failures
- Verify fallback responses are appropriate

## Troubleshooting

### Circuit Opens Too Frequently

**Problem:** Circuit breaker opens after just a few failures.

**Solutions:**
- Increase `failureRateThreshold` (e.g., from 50% to 70%)
- Increase `minimumNumberOfCalls` (e.g., from 10 to 20)
- Check if timeout is too aggressive

### Circuit Never Opens

**Problem:** Service keeps failing but circuit stays closed.

**Solutions:**
- Verify `@CircuitBreaker` annotation is present
- Check that failures are actual exceptions (not error responses)
- Ensure minimum number of calls is reached
- Review sliding window configuration

### Slow Recovery

**Problem:** Circuit takes too long to recover.

**Solutions:**
- Reduce `waitDurationInOpenState` (e.g., from 60s to 30s)
- Increase `permittedNumberOfCallsInHalfOpenState` for faster testing
- Check if downstream service is actually healthy

### Fallback Not Called

**Problem:** Fallback method is not being invoked.

**Solutions:**
- Verify fallback method signature matches original method
- Check method visibility (should be private or public, not package-private)
- Ensure exception types match
- Review logs for Resilience4j errors

## Configuration Reference

### application.yml

```yaml
# Bifrost Service Configuration
bifrost:
  base-url: ${BIFROST_BASE_URL:http://localhost:8000}

# Management Endpoints
management:
  endpoints:
    web:
      exposure:
        include: circuitbreakers,circuitbreakerevents
  health:
    circuitbreakers:
      enabled: true
```

### Resilience4jConfig.java

```java
@Configuration
public class Resilience4jConfig {
    
    @Bean
    public Customizer<Resilience4JCircuitBreakerFactory> defaultCustomizer() {
        return factory -> factory.configureDefault(id -> new Resilience4JConfigBuilder(id)
                .timeLimiterConfig(TimeLimiterConfig.custom()
                        .timeoutDuration(Duration.ofSeconds(10))
                        .build())
                .circuitBreakerConfig(CircuitBreakerConfig.custom()
                        .failureRateThreshold(50)
                        .minimumNumberOfCalls(10)
                        .waitDurationInOpenState(Duration.ofSeconds(60))
                        .permittedNumberOfCallsInHalfOpenState(3)
                        .slidingWindowSize(100)
                        .build())
                .build());
    }
}
```

## Related Documentation

- [JWT Authentication](JWT_AUTHENTICATION.md)
- [Rate Limiting](RATE_LIMITING.md) (coming soon)
- [API Documentation](API_DOCUMENTATION.md) (coming soon)
- [Resilience4j Official Docs](https://resilience4j.readme.io/)

## Support

For issues or questions:
- Check logs in `logs/heimdall.log`
- Monitor actuator endpoints
- Review Prometheus metrics
- Contact: DevOps Team
