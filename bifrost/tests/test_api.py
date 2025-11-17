"""API 테스트"""

import pytest
from fastapi.testclient import TestClient
from bifrost.api import app


client = TestClient(app)


def test_root():
    """루트 엔드포인트"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Bifrost" in response.json()["name"]


def test_health():
    """헬스 체크"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_endpoint():
    """분석 엔드포인트"""
    # Mock 데이터
    payload = {
        "log_content": "2024-10-25 ERROR Database connection failed",
        "source": "local",
        "service_name": "test-api",
        "tags": ["error", "database"],
    }
    
    # 실제 Ollama가 없으면 실패할 수 있음
    # response = client.post("/analyze", json=payload)
    # assert response.status_code in [200, 500]


def test_history_endpoint():
    """히스토리 엔드포인트"""
    payload = {
        "limit": 10,
        "offset": 0,
    }
    
    response = client.post("/history", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_metrics_endpoint():
    """메트릭 엔드포인트"""
    response = client.get("/metrics?hours=24")
    assert response.status_code == 200
    data = response.json()
    assert "total_analyses" in data
    assert "avg_duration_seconds" in data


def test_prometheus_metrics():
    """Prometheus 메트릭"""
    response = client.get("/metrics/prometheus")
    assert response.status_code == 200
    assert "bifrost_" in response.text
