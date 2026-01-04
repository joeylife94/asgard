package com.heimdall.controller;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.*;

import com.heimdall.ratelimit.RateLimiterService;

@WebMvcTest(HealthController.class)
@TestPropertySource(properties = {
    "spring.autoconfigure.exclude=" +
        "org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration," +
        "net.devh.boot.grpc.client.autoconfigure.GrpcClientAutoConfiguration," +
        "net.devh.boot.grpc.client.autoconfigure.GrpcClientHealthAutoConfiguration," +
        "net.devh.boot.grpc.server.autoconfigure.GrpcServerFactoryAutoConfiguration," +
        "net.devh.boot.grpc.server.autoconfigure.GrpcServerAutoConfiguration," +
        "net.devh.boot.grpc.server.autoconfigure.GrpcServerSecurityAutoConfiguration," +
        "net.devh.boot.grpc.server.autoconfigure.GrpcServerMetricAutoConfiguration," +
        "net.devh.boot.grpc.server.autoconfigure.GrpcMetadataEurekaConfiguration"
})
@DisplayName("HealthController Unit Tests")
class HealthControllerTest {

    @MockBean
    private RateLimiterService rateLimiterService;

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("헬스 체크 엔드포인트는 UP 상태를 반환해야 한다")
    void healthEndpoint_ShouldReturnUpStatus() throws Exception {
        mockMvc.perform(get("/api/v1/health"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(jsonPath("$.service").value("heimdall"))
                .andExpect(jsonPath("$.version").value("1.0.0"))
                .andExpect(jsonPath("$.timestamp").exists());
    }

    @Test
    @DisplayName("Echo 엔드포인트는 요청 데이터를 반환해야 한다")
    void echoEndpoint_ShouldReturnRequestData() throws Exception {
        String requestBody = "{\"message\":\"test\",\"value\":123}";
        
        mockMvc.perform(post("/api/v1/echo")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.echo.message").value("test"))
                .andExpect(jsonPath("$.echo.value").value(123))
                .andExpect(jsonPath("$.timestamp").exists())
                .andExpect(jsonPath("$.receivedAt").exists());
    }

    @Test
    @DisplayName("CPU 스트레스 엔드포인트는 정상적으로 완료되어야 한다")
    void cpuStressEndpoint_ShouldCompleteSuccessfully() throws Exception {
        mockMvc.perform(get("/api/v1/stress/cpu")
                .param("iterations", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("completed"))
                .andExpect(jsonPath("$.iterations").value(10))
                .andExpect(jsonPath("$.duration_ms").exists())
                .andExpect(jsonPath("$.result").exists());
    }

    @Test
    @DisplayName("메모리 스트레스 엔드포인트는 정상적으로 완료되어야 한다")
    void memoryStressEndpoint_ShouldCompleteSuccessfully() throws Exception {
        mockMvc.perform(get("/api/v1/stress/memory")
                .param("arraySize", "100"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("completed"))
                .andExpect(jsonPath("$.arraySize").value(100))
                .andExpect(jsonPath("$.duration_ms").exists())
                .andExpect(jsonPath("$.memoryUsed_mb").exists());
    }

    @Test
    @DisplayName("지연 엔드포인트는 요청된 시간만큼 지연되어야 한다")
    void delayEndpoint_ShouldDelayForRequestedTime() throws Exception {
        mockMvc.perform(get("/api/v1/delay")
                .param("milliseconds", "100"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("completed"))
                .andExpect(jsonPath("$.requested_delay_ms").value(100))
                .andExpect(jsonPath("$.actual_delay_ms").value(greaterThanOrEqualTo(100)))
                .andExpect(jsonPath("$.timestamp").exists());
    }

    @Test
    @DisplayName("랜덤 에러 엔드포인트는 때때로 에러를 발생시켜야 한다")
    void randomErrorEndpoint_WithHighErrorRate_ShouldEventuallyFail() throws Exception {
        // 100% 에러율로 테스트
        mockMvc.perform(get("/api/v1/random-error")
                .param("errorRate", "100"))
                .andExpect(status().is5xxServerError());
    }

    @Test
    @DisplayName("랜덤 에러 엔드포인트는 낮은 에러율에서 성공할 수 있어야 한다")
    void randomErrorEndpoint_WithLowErrorRate_CanSucceed() throws Exception {
        // 0% 에러율로 테스트
        mockMvc.perform(get("/api/v1/random-error")
                .param("errorRate", "0"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("success"))
                .andExpect(jsonPath("$.errorRate").value(0));
    }
}
