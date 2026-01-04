package com.heimdall.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.heimdall.dto.LoginRequest;
import com.heimdall.security.JwtTokenProvider;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.*;

/**
 * Integration tests for AuthController
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@DisplayName("Auth Controller Integration Tests")
class AuthControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Autowired
    private JwtTokenProvider tokenProvider;
    
    @Test
    @DisplayName("Should login with valid credentials")
    void shouldLoginWithValidCredentials() throws Exception {
        // Given
        LoginRequest loginRequest = new LoginRequest("admin", "admin123");
        
        // When & Then
        mockMvc.perform(post("/api/v1/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(loginRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token", notNullValue()))
                .andExpect(jsonPath("$.type", is("Bearer")))
                .andExpect(jsonPath("$.username", is("admin")))
                .andExpect(jsonPath("$.expiresIn", greaterThan(0)));
    }
    
    @Test
    @DisplayName("Should reject login with invalid credentials")
    void shouldRejectLoginWithInvalidCredentials() throws Exception {
        // Given
        LoginRequest loginRequest = new LoginRequest("admin", "wrongpassword");
        
        // When & Then
        mockMvc.perform(post("/api/v1/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(loginRequest)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.error", notNullValue()));
    }
    
    @Test
    @DisplayName("Should reject login with missing username")
    void shouldRejectLoginWithMissingUsername() throws Exception {
        // Given
        String invalidRequest = "{\"password\":\"admin123\"}";
        
        // When & Then
        mockMvc.perform(post("/api/v1/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidRequest))
                .andExpect(status().isBadRequest());
    }
    
    @Test
    @DisplayName("Should get current user info with valid token")
    void shouldGetCurrentUserInfoWithValidToken() throws Exception {
        // Given
        String token = tokenProvider.generateToken("admin", 
                java.util.Arrays.asList("ROLE_ADMIN", "ROLE_USER"));
        
        // When & Then
        mockMvc.perform(get("/api/v1/auth/me")
                .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username", is("admin")))
                .andExpect(jsonPath("$.authenticated", is(true)))
                .andExpect(jsonPath("$.authorities", notNullValue()));
    }
    
    @Test
    @DisplayName("Should reject access without token")
    void shouldRejectAccessWithoutToken() throws Exception {
        // When & Then
        mockMvc.perform(get("/api/v1/auth/me"))
                .andExpect(status().isUnauthorized());
    }
    
    @Test
    @DisplayName("Should validate valid token")
    void shouldValidateValidToken() throws Exception {
        // Given
        String token = tokenProvider.generateToken("user", 
                java.util.Arrays.asList("ROLE_USER"));
        
        // When & Then
        mockMvc.perform(get("/api/v1/auth/validate")
                .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.valid", is(true)))
                .andExpect(jsonPath("$.username", is("user")));
    }
    
    @Test
    @DisplayName("Should reject invalid token")
    void shouldRejectInvalidToken() throws Exception {
        // Given
        String invalidToken = "invalid.jwt.token";
        
        // When & Then
        mockMvc.perform(get("/api/v1/auth/validate")
                .header("Authorization", "Bearer " + invalidToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.valid", is(false)));
    }
    
    @Test
    @DisplayName("Should logout successfully")
    void shouldLogoutSuccessfully() throws Exception {
        // Given
        String token = tokenProvider.generateToken("user", 
                java.util.Arrays.asList("ROLE_USER"));
        
        // When & Then
        mockMvc.perform(post("/api/v1/auth/logout")
                .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message", is("Logged out successfully")));
    }
}
