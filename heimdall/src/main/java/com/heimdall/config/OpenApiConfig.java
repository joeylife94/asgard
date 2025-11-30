package com.heimdall.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

/**
 * OpenAPI Configuration for Swagger UI
 * Access Swagger UI at: http://localhost:8080/swagger-ui.html
 */
@Configuration
public class OpenApiConfig {
    
    @Value("${spring.application.name}")
    private String applicationName;
    
    @Value("${server.port}")
    private String serverPort;
    
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(apiInfo())
                .servers(List.of(
                        new Server()
                                .url("http://localhost:" + serverPort)
                                .description("Development Server"),
                        new Server()
                                .url("https://api.asgard.example.com")
                                .description("Production Server")
                ))
                .components(new Components()
                        .addSecuritySchemes("bearer-jwt", securityScheme()))
                .addSecurityItem(new SecurityRequirement().addList("bearer-jwt"));
    }
    
    private Info apiInfo() {
        return new Info()
                .title("Heimdall API Gateway")
                .version("1.0.0")
                .description("""
                        # Heimdall API Gateway
                        
                        MSA 로그 분석 플랫폼 Asgard의 API Gateway 서비스입니다.
                        
                        ## Features
                        
                        - **JWT Authentication**: 토큰 기반 인증 시스템
                        - **Circuit Breaker**: Resilience4j 기반 장애 격리
                        - **Rate Limiting**: Redis 기반 API 속도 제한
                        - **Log Analysis**: Bifrost ML/AI 서비스 연동
                        
                        ## Getting Started
                        
                        1. POST `/api/auth/login` 로 JWT 토큰 획득
                        2. `Authorization: Bearer <token>` 헤더로 API 호출
                        3. Rate Limit 헤더를 확인하여 사용량 모니터링
                        
                        ## Rate Limits
                        
                        - `/api/bifrost/analyze`: 100 requests/hour
                        - `/api/bifrost/history`: 200 requests/hour
                        
                        ## Default Users
                        
                        - **admin** / admin123 (ROLE_ADMIN)
                        - **developer** / dev123 (ROLE_DEVELOPER)
                        - **user** / user123 (ROLE_USER)
                        """)
                .contact(new Contact()
                        .name("Asgard Team")
                        .email("support@asgard.example.com")
                        .url("https://github.com/yourusername/asgard"))
                .license(new License()
                        .name("MIT License")
                        .url("https://opensource.org/licenses/MIT"));
    }
    
    private SecurityScheme securityScheme() {
        return new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")
                .description("""
                        JWT 인증 토큰을 입력하세요.
                        
                        토큰 획득 방법:
                        1. POST /api/auth/login 호출
                        2. 응답에서 accessToken 추출
                        3. "Bearer " 접두사 없이 토큰만 입력
                        """);
    }
}
