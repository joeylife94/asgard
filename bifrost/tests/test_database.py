"""데이터베이스 테스트"""

import pytest
from bifrost.database import Database


def test_save_and_get_analysis(test_db):
    """분석 저장 및 조회"""
    analysis_id = test_db.save_analysis(
        source="local",
        model="mistral",
        log_content="test log",
        response="test response",
        duration=1.5,
        tags=["test"],
        service_name="test-service",
    )
    
    assert analysis_id > 0
    
    result = test_db.get_analysis(analysis_id)
    assert result is not None
    assert result["source"] == "local"
    assert result["model"] == "mistral"
    assert result["service_name"] == "test-service"


def test_list_analyses(test_db):
    """분석 목록 조회"""
    # 여러 개 저장
    for i in range(5):
        test_db.save_analysis(
            source="local",
            model="mistral",
            log_content=f"log {i}",
            response=f"response {i}",
            duration=1.0,
            service_name=f"service-{i}",
        )
    
    results = test_db.list_analyses(limit=10)
    assert len(results) >= 5


def test_duplicate_detection(test_db):
    """중복 분석 감지"""
    log_content = "duplicate test log"
    
    # 첫 번째 분석
    id1 = test_db.save_analysis(
        source="local",
        model="mistral",
        log_content=log_content,
        response="response 1",
        duration=1.0,
    )
    
    # 두 번째 분석 (동일 로그)
    id2 = test_db.save_analysis(
        source="local",
        model="mistral",
        log_content=log_content,
        response="response 2",
        duration=1.0,
    )
    
    # 중복 찾기
    import hashlib
    log_hash = hashlib.sha256(log_content.encode()).hexdigest()
    duplicates = test_db.get_duplicate_analyses(log_hash, hours=1)
    
    assert len(duplicates) == 2


def test_metrics_summary(test_db):
    """메트릭 요약"""
    # 분석 추가
    for i in range(3):
        test_db.save_analysis(
            source="local",
            model="mistral",
            log_content=f"log {i}",
            response=f"response {i}",
            duration=i + 1.0,
        )
    
    summary = test_db.get_metrics_summary(hours=24)
    assert summary["total_analyses"] >= 3
    assert summary["avg_duration_seconds"] > 0


def test_api_key_creation(test_db):
    """API 키 생성 및 검증"""
    key = test_db.create_api_key(
        name="test-key",
        rate_limit=100,
        description="Test API key",
    )
    
    assert len(key) > 20
    assert test_db.validate_api_key(key) is True
    assert test_db.validate_api_key("invalid-key") is False
