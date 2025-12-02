"""
Integration Tests for Two-Track AI System
==========================================

End-to-end tests verifying automatic routing between:
- Track A (Local Ollama): Sensitive data
- Track B (Cloud Bedrock): General data
"""

import pytest
from bifrost.router import get_router, SensitivityLevel


class TestTwoTrackIntegration:
    """통합 테스트: Two-Track AI 자동 라우팅"""
    
    @pytest.fixture
    def router(self):
        return get_router()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Track A Scenarios (민감 데이터 → Local Ollama)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_scenario_gdpr_violation(self, router):
        """
        시나리오 1: GDPR 위반 가능성 로그
        
        EU 고객 개인정보 포함 → Track A (Local)
        """
        log = """
        [ERROR] 2024-01-15 14:23:45
        EU Customer Registration Failed
        Email: customer@example.de
        GDPR consent: not provided
        IP: 192.168.1.100
        Session: abc123
        """
        
        result = router.route(log)
        
        assert result["track"] == "local", "GDPR 데이터는 Track A (Local)로 라우팅되어야 함"
        assert result["sensitivity"] in ("high", "medium")
        assert "Privacy-sensitive" in result["reason"] or "GDPR" in str(result["detected_patterns"])
    
    def test_scenario_payment_failure(self, router):
        """
        시나리오 2: 결제 실패 로그 (금융 정보)
        
        카드 번호 포함 → Track A (Local)
        """
        log = """
        [PAYMENT] Transaction failed
        Card: 4532-1234-5678-9010
        Amount: 99.99 EUR
        Error: Insufficient funds
        User: john@example.com
        """
        
        result = router.route(log)
        
        assert result["track"] == "local"
        assert result["sensitivity"] == "high"
    
    def test_scenario_authentication_log(self, router):
        """
        시나리오 3: 인증 실패 로그 (크레덴셜)
        
        비밀번호/토큰 포함 → Track A (Local)
        """
        log = """
        2024-01-15 10:30:00 [AUTH] Login failed
        Username: admin
        Password: admin123
        Reason: Invalid credentials
        """
        
        result = router.route(log)
        
        assert result["track"] == "local"
        assert result["sensitivity"] == "high"
    
    def test_scenario_internal_network(self, router):
        """
        시나리오 4: 내부 네트워크 로그
        
        Private IP, 세션 ID → Track A (Local)
        """
        log = """
        [NETWORK] Connection established
        Source: 10.0.5.23
        Destination: 172.16.0.100
        Session ID: xyz789abc
        Protocol: HTTPS
        """
        
        result = router.route(log)
        
        assert result["track"] == "local"
        assert result["sensitivity"] == "medium"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Track B Scenarios (일반 데이터 → Cloud Bedrock)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_scenario_application_error(self, router):
        """
        시나리오 5: 일반 애플리케이션 에러
        
        민감정보 없음 → Track B (Cloud)
        """
        log = """
        2024-01-15 11:45:00 ERROR [main] com.example.UserService
        java.lang.NullPointerException: Cannot invoke "String.length()" on null
            at com.example.UserService.processUser(UserService.java:42)
            at com.example.UserController.handleRequest(UserController.java:15)
        """
        
        result = router.route(log)
        
        assert result["track"] == "cloud", "일반 에러는 Track B (Cloud)로 라우팅되어야 함"
        assert result["sensitivity"] == "low"
        assert "cost efficiency" in result["reason"]
    
    def test_scenario_performance_metrics(self, router):
        """
        시나리오 6: 성능 메트릭 로그
        
        시스템 모니터링 데이터 → Track B (Cloud)
        """
        log = """
        [METRICS] Application Performance Report
        - Requests/sec: 1523
        - Avg latency: 145ms
        - Error rate: 0.02%
        - CPU usage: 45%
        - Memory: 2.1GB / 8GB
        - Active threads: 120
        """
        
        result = router.route(log)
        
        assert result["track"] == "cloud"
        assert result["sensitivity"] == "low"
    
    def test_scenario_info_startup(self, router):
        """
        시나리오 7: 애플리케이션 시작 로그
        
        일반 정보성 로그 → Track B (Cloud)
        """
        log = """
        2024-01-15 08:00:00 INFO [main] com.example.Application
        Starting Application v2.1.0
        Java version: 21.0.1
        Spring Boot: 3.3.5
        Profiles: production
        Port: 8080
        """
        
        result = router.route(log)
        
        assert result["track"] == "cloud"
        assert result["sensitivity"] == "low"
    
    def test_scenario_public_api_call(self, router):
        """
        시나리오 8: Public API 호출 로그
        
        Public IP만 포함 → Track B (Cloud)
        """
        log = """
        [API] External request received
        From: 203.0.113.42 (Public CDN)
        Endpoint: /api/v1/health
        Method: GET
        Status: 200 OK
        Duration: 15ms
        """
        
        result = router.route(log)
        
        assert result["track"] == "cloud"
        assert result["sensitivity"] == "low"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Mixed Content Tests
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_scenario_mixed_high_wins(self, router):
        """
        시나리오 9: 혼합 컨텐츠 (HIGH 우선순위)
        
        일반 로그 + 이메일 → Track A (Local)
        """
        log = """
        INFO: Processing batch job
        ERROR: Notification failed for user@example.com
        Retrying in 60 seconds...
        """
        
        result = router.route(log)
        
        # HIGH sensitivity (email) takes priority
        assert result["track"] == "local"
        assert result["sensitivity"] == "high"
    
    def test_scenario_borderline_case(self, router):
        """
        시나리오 10: 경계 사례 (숫자 많은 일반 로그)
        
        숫자 포함하지만 민감정보 아님 → Track B (Cloud)
        """
        log = """
        [REPORT] Daily Statistics
        Total orders: 1234
        Revenue: 5678 USD
        New users: 90
        Page views: 123456
        """
        
        result = router.route(log)
        
        assert result["track"] == "cloud"
        assert result["sensitivity"] == "low"


class TestRouterMetrics:
    """라우팅 메트릭 테스트"""
    
    def test_routing_distribution(self):
        """라우팅 분포 확인"""
        router = get_router()
        
        test_cases = [
            ("email@example.com in logs", "local"),
            ("General application log", "cloud"),
            ("password: secret123", "local"),
            ("INFO: Service started", "cloud"),
            ("Internal IP: 192.168.1.1", "local"),
            ("Public IP: 8.8.8.8", "cloud"),
            ("GDPR compliance check", "local"),
            ("Performance metrics", "cloud"),
        ]
        
        local_count = 0
        cloud_count = 0
        
        for log, expected in test_cases:
            result = router.route(log)
            assert result["track"] == expected, f"Failed for: {log}"
            
            if result["track"] == "local":
                local_count += 1
            else:
                cloud_count += 1
        
        # 분포 확인: 50-50 정도 예상
        assert local_count == 4, "Track A (Local) 라우팅 수"
        assert cloud_count == 4, "Track B (Cloud) 라우팅 수"


class TestEdgeCases:
    """엣지 케이스 테스트"""
    
    def test_empty_log(self):
        """빈 로그 → Track B (Cloud)"""
        router = get_router()
        result = router.route("")
        assert result["track"] == "cloud"
    
    def test_very_long_log(self):
        """매우 긴 로그"""
        router = get_router()
        log = "INFO: " + ("x" * 10000) + " email@example.com"
        result = router.route(log)
        assert result["track"] == "local"  # Email detected
    
    def test_unicode_with_email(self):
        """유니코드 + 이메일"""
        router = get_router()
        log = "사용자 user@example.com 로그인 실패"
        result = router.route(log)
        assert result["track"] == "local"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
