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
    
    // NOTE: Heimdall <-> Bifrost analysis execution is Kafka-only.
    // REST is intentionally kept for health/debug/manual admin only.
}
