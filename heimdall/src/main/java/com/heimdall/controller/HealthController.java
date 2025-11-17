package com.heimdall.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Health Check and Test Controller
 * 테스트 및 모니터링을 위한 기본 엔드포인트
 */
@Slf4j
@RestController
@RequestMapping("/api/v1")
public class HealthController {

    /**
     * 기본 헬스 체크
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("timestamp", LocalDateTime.now());
        response.put("service", "heimdall");
        response.put("version", "1.0.0");
        return ResponseEntity.ok(response);
    }

    /**
     * Echo 테스트 (요청 데이터 반환)
     */
    @PostMapping("/echo")
    public ResponseEntity<Map<String, Object>> echo(@RequestBody Map<String, Object> payload) {
        log.info("Echo request received: {}", payload);
        Map<String, Object> response = new HashMap<>();
        response.put("echo", payload);
        response.put("timestamp", LocalDateTime.now());
        response.put("receivedAt", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }

    /**
     * CPU 부하 테스트용 엔드포인트
     */
    @GetMapping("/stress/cpu")
    public ResponseEntity<Map<String, Object>> cpuStress(
            @RequestParam(defaultValue = "100") int iterations) {
        long start = System.currentTimeMillis();
        
        // CPU 집약적 작업
        double result = 0;
        for (int i = 0; i < iterations * 10000; i++) {
            result += Math.sqrt(i) * Math.sin(i);
        }
        
        long duration = System.currentTimeMillis() - start;
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "completed");
        response.put("iterations", iterations);
        response.put("duration_ms", duration);
        response.put("result", result);
        return ResponseEntity.ok(response);
    }

    /**
     * 메모리 부하 테스트용 엔드포인트
     */
    @GetMapping("/stress/memory")
    public ResponseEntity<Map<String, Object>> memoryStress(
            @RequestParam(defaultValue = "1000") int arraySize) {
        long start = System.currentTimeMillis();
        
        // 메모리 할당
        int[][] array = new int[arraySize][arraySize];
        for (int i = 0; i < arraySize; i++) {
            for (int j = 0; j < arraySize; j++) {
                array[i][j] = i * j;
            }
        }
        
        long duration = System.currentTimeMillis() - start;
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "completed");
        response.put("arraySize", arraySize);
        response.put("duration_ms", duration);
        response.put("memoryUsed_mb", (arraySize * arraySize * 4) / 1024 / 1024);
        return ResponseEntity.ok(response);
    }

    /**
     * 지연 시뮬레이션 (타임아웃 테스트용)
     */
    @GetMapping("/delay")
    public ResponseEntity<Map<String, Object>> delay(
            @RequestParam(defaultValue = "1000") long milliseconds) throws InterruptedException {
        long start = System.currentTimeMillis();
        Thread.sleep(milliseconds);
        long duration = System.currentTimeMillis() - start;
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "completed");
        response.put("requested_delay_ms", milliseconds);
        response.put("actual_delay_ms", duration);
        response.put("timestamp", LocalDateTime.now());
        return ResponseEntity.ok(response);
    }

    /**
     * 랜덤 에러 생성 (Circuit Breaker 테스트용)
     */
    @GetMapping("/random-error")
    public ResponseEntity<Map<String, Object>> randomError(
            @RequestParam(defaultValue = "50") int errorRate) {
        if (Math.random() * 100 < errorRate) {
            throw new RuntimeException("Simulated random error for testing");
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("errorRate", errorRate);
        response.put("timestamp", LocalDateTime.now());
        return ResponseEntity.ok(response);
    }
}
