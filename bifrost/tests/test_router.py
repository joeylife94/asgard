"""
Privacy Router Unit Tests
==========================

Tests for GDPR-compliant intelligent routing logic.
"""

import pytest
from bifrost.router import PrivacyRouter, Track, SensitivityLevel, get_router


class TestPrivacyRouter:
    """Test Privacy Router classification and routing."""
    
    @pytest.fixture
    def router(self):
        """Create router instance for testing."""
        return PrivacyRouter()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HIGH Sensitivity Tests (Track A)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_email_detection_high(self, router):
        """Test email address detection → HIGH sensitivity."""
        log = "User john.doe@example.com logged in successfully"
        sensitivity, detected = router.classify_sensitivity(log)
        
        assert sensitivity == SensitivityLevel.HIGH
        assert any("HIGH" in d for d in detected)
    
    def test_credit_card_detection_high(self, router):
        """Test credit card number detection → HIGH sensitivity."""
        log = "Payment failed for card 4532-1234-5678-9010"
        sensitivity, _ = router.classify_sensitivity(log)
        
        assert sensitivity == SensitivityLevel.HIGH
    
    def test_password_detection_high(self, router):
        """Test password/token detection → HIGH sensitivity."""
        logs = [
            "password: MySecretP@ss123",
            "api_key=sk_live_123456789abcdef",
            "Authorization: Bearer eyJhbGciOiJIUzI1NiIs",
            "JWT token: eyJzdWIiOiIxMjM0NTY3ODkwIn0",
        ]
        
        for log in logs:
            sensitivity, _ = router.classify_sensitivity(log)
            assert sensitivity == SensitivityLevel.HIGH, f"Failed for: {log}"
    
    def test_gdpr_keywords_high(self, router):
        """Test GDPR keywords → HIGH sensitivity."""
        logs = [
            "Processing personal data for EU customer",
            "GDPR compliance check required",
            "Data subject requested right to erasure",
            "Consent form submitted by user",
        ]
        
        for log in logs:
            sensitivity, _ = router.classify_sensitivity(log)
            assert sensitivity == SensitivityLevel.HIGH, f"Failed for: {log}"
    
    def test_financial_info_high(self, router):
        """Test financial identifiers → HIGH sensitivity."""
        logs = [
            "IBAN: DE89370400440532013000 validated",
            "SWIFT code: DEUTDEFF provided",
            "account_number: 1234567890 debited",
        ]
        
        for log in logs:
            sensitivity, _ = router.classify_sensitivity(log)
            assert sensitivity == SensitivityLevel.HIGH, f"Failed for: {log}"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEDIUM Sensitivity Tests (Track A)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_internal_ip_detection_medium(self, router):
        """Test private IP detection → MEDIUM sensitivity."""
        logs = [
            "Connection from 10.0.0.5 established",
            "Server 172.16.0.100 responded",
            "Internal host 192.168.1.50 unreachable",
        ]
        
        for log in logs:
            sensitivity, _ = router.classify_sensitivity(log)
            assert sensitivity == SensitivityLevel.MEDIUM, f"Failed for: {log}"
    
    def test_session_id_detection_medium(self, router):
        """Test session/user ID detection → MEDIUM sensitivity."""
        logs = [
            "user_id: 12345 accessed dashboard",
            "session_id=abc123def456 expired",
            "x-request-id: 9f8e7d6c-5b4a-3210-fedc-ba9876543210",
            "Cookie: session=MTIzNDU2Nzg5MA; path=/",
        ]
        
        for log in logs:
            sensitivity, _ = router.classify_sensitivity(log)
            assert sensitivity == SensitivityLevel.MEDIUM, f"Failed for: {log}"
    
    def test_database_connection_medium(self, router):
        """Test DB connection strings → MEDIUM sensitivity."""
        logs = [
            "jdbc:mysql://10.0.0.5:3306/mydb",
            "mongodb://localhost:27017/analytics",
            "jdbc:postgresql://172.16.0.10:5432/users",
        ]
        
        for log in logs:
            sensitivity, _ = router.classify_sensitivity(log)
            assert sensitivity == SensitivityLevel.MEDIUM, f"Failed for: {log}"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LOW Sensitivity Tests (Track B)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_general_logs_low(self, router):
        """Test general system logs → LOW sensitivity."""
        logs = [
            "Application started successfully",
            "ERROR: NullPointerException at line 42",
            "INFO: Processing 1000 records",
            "WARN: High memory usage detected (85%)",
            "Request completed in 250ms",
        ]
        
        for log in logs:
            sensitivity, _ = router.classify_sensitivity(log)
            assert sensitivity == SensitivityLevel.LOW, f"Failed for: {log}"
    
    def test_public_ip_low(self, router):
        """Test public IP addresses → LOW sensitivity."""
        logs = [
            "Public IP 8.8.8.8 resolved",
            "External host 1.2.3.4 connected",
            "CDN 203.0.113.0 serving assets",
        ]
        
        for log in logs:
            sensitivity, _ = router.classify_sensitivity(log)
            assert sensitivity == SensitivityLevel.LOW, f"Failed for: {log}"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Routing Decision Tests
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_route_high_to_local(self, router):
        """Test HIGH sensitivity routes to Track A (local)."""
        log = "User email: sensitive@example.com in logs"
        result = router.route(log)
        
        assert result["track"] == "local"
        assert result["sensitivity"] == "high"
        assert "Privacy-sensitive" in result["reason"]
    
    def test_route_medium_to_local(self, router):
        """Test MEDIUM sensitivity routes to Track A (local)."""
        log = "Connection from 192.168.0.100 accepted"
        result = router.route(log)
        
        assert result["track"] == "local"
        assert result["sensitivity"] == "medium"
    
    def test_route_low_to_cloud(self, router):
        """Test LOW sensitivity routes to Track B (cloud)."""
        log = "INFO: Service health check passed"
        result = router.route(log)
        
        assert result["track"] == "cloud"
        assert result["sensitivity"] == "low"
        assert "cost efficiency" in result["reason"]
    
    def test_detected_patterns_in_result(self, router):
        """Test detected patterns are included in routing result."""
        log = "password: secret123"
        result = router.route(log)
        
        assert "detected_patterns" in result
        assert len(result["detected_patterns"]) > 0
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Edge Cases & Mixed Content
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_mixed_content_high_priority(self, router):
        """Test mixed content prioritizes highest sensitivity."""
        log = """
        INFO: Application started
        User john@example.com logged in from 192.168.0.5
        Session created successfully
        """
        result = router.route(log)
        
        # Email (HIGH) should take priority over IP (MEDIUM)
        assert result["sensitivity"] == "high"
        assert result["track"] == "local"
    
    def test_empty_content(self, router):
        """Test empty content → LOW sensitivity."""
        sensitivity, _ = router.classify_sensitivity("")
        assert sensitivity == SensitivityLevel.LOW
    
    def test_korean_log_with_email(self, router):
        """Test Korean logs with sensitive data → HIGH sensitivity."""
        log = "사용자 user@example.com이(가) 로그인했습니다"
        sensitivity, _ = router.classify_sensitivity(log)
        
        assert sensitivity == SensitivityLevel.HIGH
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Singleton & Utility Tests
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_singleton_router(self):
        """Test get_router() returns singleton instance."""
        router1 = get_router()
        router2 = get_router()
        
        assert router1 is router2
    
    def test_explain_route_output(self, router):
        """Test explain_route returns formatted explanation."""
        log = "password: test123"
        explanation = router.explain_route(log)
        
        assert "Track" in explanation
        assert "Sensitivity" in explanation
        assert "Reason" in explanation
        assert "Ollama" in explanation  # HIGH → local


class TestRealWorldScenarios:
    """Test with real-world log examples."""
    
    @pytest.fixture
    def router(self):
        return PrivacyRouter()
    
    def test_spring_boot_exception_low(self, router):
        """Test Spring Boot exception logs → LOW (no sensitive data)."""
        log = """
        2024-01-15 10:23:45.123 ERROR [http-nio-8080-exec-1] 
        o.a.c.c.C.[.[.[/].[dispatcherServlet] : 
        Servlet.service() for servlet [dispatcherServlet] threw exception
        java.lang.NullPointerException: Cannot invoke String.length() on null
            at com.example.UserService.processUser(UserService.java:42)
        """
        result = router.route(log)
        assert result["track"] == "cloud"
    
    def test_authentication_log_high(self, router):
        """Test auth logs with credentials → HIGH."""
        log = """
        2024-01-15 10:25:00 INFO  AuthController - Login attempt
        Username: admin
        Password: admin123
        IP: 203.0.113.5
        Result: FAILED
        """
        result = router.route(log)
        assert result["track"] == "local"
        assert result["sensitivity"] == "high"
    
    def test_api_request_with_token_high(self, router):
        """Test API logs with Bearer token → HIGH."""
        log = """
        POST /api/v1/users HTTP/1.1
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
        Content-Type: application/json
        """
        result = router.route(log)
        assert result["track"] == "local"
    
    def test_performance_metrics_low(self, router):
        """Test performance metrics → LOW."""
        log = """
        [METRICS] 2024-01-15 10:30:00
        - Request count: 1523
        - Avg response time: 145ms
        - Error rate: 0.02%
        - CPU usage: 45%
        - Memory: 2.1GB / 8GB
        """
        result = router.route(log)
        assert result["track"] == "cloud"
