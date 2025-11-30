package com.heimdall.dto;

/**
 * JWT Token Response DTO
 */
public record TokenResponse(
        String token,
        String type,
        long expiresIn,
        String username
) {
    public TokenResponse(String token, long expiresIn, String username) {
        this(token, "Bearer", expiresIn, username);
    }
}
