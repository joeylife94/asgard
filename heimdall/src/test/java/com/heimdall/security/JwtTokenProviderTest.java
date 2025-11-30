package com.heimdall.security;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;

import java.util.Arrays;
import java.util.Collection;
import java.util.Base64;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Unit tests for JwtTokenProvider
 */
@DisplayName("JWT Token Provider Tests")
class JwtTokenProviderTest {
    
    private JwtTokenProvider tokenProvider;
    
    private static final String TEST_SECRET = Base64.getEncoder()
            .encodeToString("testSecretKeyForJwtTokenGenerationAtLeast256BitsLong12345678".getBytes());
    private static final long TOKEN_VALIDITY = 3600; // 1 hour
    
    @BeforeEach
    void setUp() {
        tokenProvider = new JwtTokenProvider(TEST_SECRET, TOKEN_VALIDITY);
    }
    
    @Test
    @DisplayName("Should generate valid JWT token from Authentication")
    void shouldGenerateTokenFromAuthentication() {
        // Given
        Collection<SimpleGrantedAuthority> authorities = Arrays.asList(
                new SimpleGrantedAuthority("ROLE_USER"),
                new SimpleGrantedAuthority("ROLE_ADMIN")
        );
        Authentication authentication = new UsernamePasswordAuthenticationToken(
                "testuser", "password", authorities);
        
        // When
        String token = tokenProvider.generateToken(authentication);
        
        // Then
        assertThat(token).isNotNull();
        assertThat(token).isNotEmpty();
        assertThat(tokenProvider.validateToken(token)).isTrue();
    }
    
    @Test
    @DisplayName("Should generate valid JWT token from username and roles")
    void shouldGenerateTokenFromUsernameAndRoles() {
        // Given
        String username = "testuser";
        Collection<String> roles = Arrays.asList("ROLE_USER", "ROLE_ADMIN");
        
        // When
        String token = tokenProvider.generateToken(username, roles);
        
        // Then
        assertThat(token).isNotNull();
        assertThat(token).isNotEmpty();
        assertThat(tokenProvider.validateToken(token)).isTrue();
    }
    
    @Test
    @DisplayName("Should extract username from token")
    void shouldExtractUsernameFromToken() {
        // Given
        String username = "testuser";
        Collection<String> roles = Arrays.asList("ROLE_USER");
        String token = tokenProvider.generateToken(username, roles);
        
        // When
        String extractedUsername = tokenProvider.getUsernameFromToken(token);
        
        // Then
        assertThat(extractedUsername).isEqualTo(username);
    }
    
    @Test
    @DisplayName("Should extract authorities from token")
    void shouldExtractAuthoritiesFromToken() {
        // Given
        String username = "testuser";
        Collection<String> roles = Arrays.asList("ROLE_USER", "ROLE_ADMIN");
        String token = tokenProvider.generateToken(username, roles);
        
        // When
        Collection<?> authorities = tokenProvider.getAuthoritiesFromToken(token);
        
        // Then
        assertThat(authorities).hasSize(2);
        assertThat(authorities.toString()).contains("ROLE_USER", "ROLE_ADMIN");
    }
    
    @Test
    @DisplayName("Should reject invalid token")
    void shouldRejectInvalidToken() {
        // Given
        String invalidToken = "invalid.jwt.token";
        
        // When
        boolean isValid = tokenProvider.validateToken(invalidToken);
        
        // Then
        assertThat(isValid).isFalse();
    }
    
    @Test
    @DisplayName("Should reject malformed token")
    void shouldRejectMalformedToken() {
        // Given
        String malformedToken = "malformed";
        
        // When
        boolean isValid = tokenProvider.validateToken(malformedToken);
        
        // Then
        assertThat(isValid).isFalse();
    }
    
    @Test
    @DisplayName("Should return correct token validity")
    void shouldReturnCorrectTokenValidity() {
        // When
        long validity = tokenProvider.getTokenValidityInMilliseconds();
        
        // Then
        assertThat(validity).isEqualTo(TOKEN_VALIDITY * 1000);
    }
}
