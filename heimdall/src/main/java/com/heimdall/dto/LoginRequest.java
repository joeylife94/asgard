package com.heimdall.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * Login Request DTO
 */
public record LoginRequest(
        @NotBlank(message = "Username is required")
        String username,
        
        @NotBlank(message = "Password is required")
        String password
) {}
