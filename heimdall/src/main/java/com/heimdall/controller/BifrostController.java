package com.heimdall.controller;

import com.heimdall.ratelimit.RateLimit;
import com.heimdall.service.BifrostClientService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Bifrost Integration Controller
 * Provides REST endpoints for ML/AI log analysis
 */
@RestController
@RequestMapping("/api/bifrost")
@Tag(name = "Bifrost Integration", description = "ML/AI log analysis service integration")
@SecurityRequirement(name = "bearer-jwt")
public class BifrostController {
    
    private final BifrostClientService bifrostService;
    
    public BifrostController(BifrostClientService bifrostService) {
        this.bifrostService = bifrostService;
    }
    
    /**
     * Health check endpoint
     * 
     * GET /api/bifrost/health
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> checkHealth() {
        Map<String, Object> health = bifrostService.checkHealth();
        return ResponseEntity.ok(health);
    }
    
    /**
     * Analyze log endpoint (synchronous)
     * 
     * POST /api/bifrost/analyze
     * Body: { "log": "error message", "level": "ERROR", ... }
     * 
     * Rate Limit: 100 requests per hour per user
     */
    @PostMapping("/analyze")
    @PreAuthorize("hasAnyRole('DEVELOPER', 'ADMIN')")
    @RateLimit(maxRequests = 100, duration = 1, timeUnit = ChronoUnit.HOURS)
    public ResponseEntity<Map<String, Object>> analyzeLog(@RequestBody Map<String, Object> logData) {
        Map<String, Object> result = bifrostService.analyzeLog(logData);
        return ResponseEntity.ok(result);
    }
    
    /**
     * Analyze log endpoint (asynchronous)
     * 
     * POST /api/bifrost/analyze/async
     * 
     * Rate Limit: 100 requests per hour per user
     */
    @PostMapping("/analyze/async")
    @PreAuthorize("hasAnyRole('DEVELOPER', 'ADMIN')")
    @RateLimit(maxRequests = 100, duration = 1, timeUnit = ChronoUnit.HOURS)
    public CompletableFuture<ResponseEntity<Map<String, Object>>> analyzeLogAsync(
            @RequestBody Map<String, Object> logData) {
        return bifrostService.analyzeLogAsync(logData)
                .thenApply(ResponseEntity::ok);
    }
    
    /**
     * Get analysis history
     * 
     * GET /api/bifrost/history?page=0&size=20
     * 
     * Rate Limit: 200 requests per hour per user
     */
    @GetMapping("/history")
    @PreAuthorize("hasAnyRole('DEVELOPER', 'ADMIN')")
    @RateLimit(maxRequests = 200, duration = 1, timeUnit = ChronoUnit.HOURS)
    public ResponseEntity<Map<String, Object>> getHistory(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Map<String, Object> history = bifrostService.getAnalysisHistory(page, size);
        return ResponseEntity.ok(history);
    }
}
