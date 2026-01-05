package com.heimdall.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import io.jsonwebtoken.security.SecurityException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Collection;
import java.util.Date;
import java.util.stream.Collectors;

/**
 * JWT Token Provider
 * Handles JWT token generation, validation, and parsing
 */
@Component
public class JwtTokenProvider {
    
    private static final Logger logger = LoggerFactory.getLogger(JwtTokenProvider.class);
    
    private final SecretKey key;
    private final long tokenValidityInMilliseconds;
    
    public JwtTokenProvider(
            @Value("${jwt.secret}") String secretKey,
            @Value("${jwt.token-validity-in-seconds:86400}") long tokenValidityInSeconds) {
        byte[] keyBytes = deriveSigningKeyBytes(secretKey);
        this.key = Keys.hmacShaKeyFor(keyBytes);
        this.tokenValidityInMilliseconds = tokenValidityInSeconds * 1000;
    }

    private static byte[] deriveSigningKeyBytes(String secretKey) {
        if (secretKey == null || secretKey.isBlank()) {
            throw new IllegalArgumentException("jwt.secret must be set");
        }

        try {
            byte[] decoded = Decoders.BASE64.decode(secretKey);
            // HS512 requires >= 512 bits (64 bytes). If decoded is shorter, derive fixed-length key material.
            if (decoded.length >= 64) {
                return decoded;
            }
            return sha512(decoded);
        } catch (Exception ignored) {
            // Accept non-base64 secrets by deriving fixed-length key material.
            return sha512(secretKey.getBytes(StandardCharsets.UTF_8));
        }
    }

    private static byte[] sha512(byte[] input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-512");
            return digest.digest(input);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-512 not available", e);
        }
    }
    
    /**
     * Generate JWT token from Authentication
     */
    public String generateToken(Authentication authentication) {
        String authorities = authentication.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.joining(","));
        
        long now = System.currentTimeMillis();
        Date validity = new Date(now + this.tokenValidityInMilliseconds);
        
        return Jwts.builder()
                .subject(authentication.getName())
                .claim("auth", authorities)
                .issuedAt(new Date(now))
                .expiration(validity)
                .signWith(key, Jwts.SIG.HS512)
                .compact();
    }
    
    /**
     * Generate JWT token with username and roles
     */
    public String generateToken(String username, Collection<String> roles) {
        String authorities = String.join(",", roles);
        
        long now = System.currentTimeMillis();
        Date validity = new Date(now + this.tokenValidityInMilliseconds);
        
        return Jwts.builder()
                .subject(username)
                .claim("auth", authorities)
                .issuedAt(new Date(now))
                .expiration(validity)
                .signWith(key, Jwts.SIG.HS512)
                .compact();
    }
    
    /**
     * Validate JWT token
     */
    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token);
            return true;
        } catch (SecurityException | MalformedJwtException e) {
            logger.error("Invalid JWT signature: {}", e.getMessage());
        } catch (ExpiredJwtException e) {
            logger.error("JWT token is expired: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            logger.error("JWT token is unsupported: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            logger.error("JWT claims string is empty: {}", e.getMessage());
        }
        return false;
    }
    
    /**
     * Get username from JWT token
     */
    public String getUsernameFromToken(String token) {
        Claims claims = Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
        
        return claims.getSubject();
    }
    
    /**
     * Get authorities from JWT token
     */
    public Collection<? extends GrantedAuthority> getAuthoritiesFromToken(String token) {
        Claims claims = Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
        
        String authorities = claims.get("auth", String.class);
        
        if (authorities == null || authorities.isEmpty()) {
            return java.util.Collections.emptyList();
        }
        
        return java.util.Arrays.stream(authorities.split(","))
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());
    }
    
    /**
     * Get token expiration time in milliseconds
     */
    public long getTokenValidityInMilliseconds() {
        return tokenValidityInMilliseconds;
    }
}
