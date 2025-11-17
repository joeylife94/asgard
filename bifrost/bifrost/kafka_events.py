"""Kafka Event Schema - Heimdall과의 MSA 통신용 이벤트 모델"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class AnalysisPriority(str, Enum):
    """분석 우선순위"""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SeverityLevel(str, Enum):
    """로그 심각도"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class AnalysisRequestEvent(BaseModel):
    """
    Heimdall로부터 받는 분석 요청 이벤트
    Topic: analysis.request
    """
    
    request_id: str = Field(..., description="요청 고유 ID (UUID)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    log_id: int = Field(..., description="Heimdall의 로그 ID")
    log_content: str = Field(..., description="분석할 로그 내용")
    service_name: str = Field(..., description="로그 출처 서비스명")
    environment: str = Field(..., description="환경 (dev/staging/prod)")
    analysis_type: str = Field(default="error", description="분석 유형")
    priority: AnalysisPriority = Field(default=AnalysisPriority.NORMAL)
    callback_topic: str = Field(default="analysis.result")
    correlation_id: str = Field(..., description="추적용 Correlation ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-11-12T10:30:00Z",
                "log_id": 12345,
                "log_content": "ERROR: Connection timeout to database",
                "service_name": "user-service",
                "environment": "production",
                "analysis_type": "error",
                "priority": "HIGH",
                "callback_topic": "analysis.result",
                "correlation_id": "corr-123456"
            }
        }


class AnalysisResultData(BaseModel):
    """AI 분석 결과 데이터"""
    summary: str = Field(..., description="분석 요약")
    root_cause: str = Field(..., description="근본 원인")
    recommendation: str = Field(..., description="해결 권장사항")
    severity: str = Field(..., description="심각도 (LOW/MEDIUM/HIGH/CRITICAL)")
    confidence: Decimal = Field(..., ge=0, le=1, description="신뢰도 (0~1)")


class AnalysisResultEvent(BaseModel):
    """
    Heimdall로 보내는 분석 결과 이벤트
    Topic: analysis.result
    """
    
    request_id: str = Field(..., description="원본 요청 ID")
    correlation_id: str = Field(..., description="Correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    log_id: int = Field(..., description="Heimdall의 로그 ID")
    analysis_result: AnalysisResultData
    bifrost_analysis_id: int = Field(..., description="Bifrost 분석 ID")
    model: str = Field(..., description="사용된 AI 모델")
    duration_seconds: Decimal = Field(..., description="분석 소요 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "correlation_id": "corr-123456",
                "timestamp": "2024-11-12T10:30:15Z",
                "log_id": 12345,
                "analysis_result": {
                    "summary": "PostgreSQL 연결 타임아웃 발생",
                    "root_cause": "Connection pool 고갈로 인한 연결 대기 시간 초과",
                    "recommendation": "max_connections 설정 증가 및 connection pool 크기 조정 권장",
                    "severity": "HIGH",
                    "confidence": 0.95
                },
                "bifrost_analysis_id": 789,
                "model": "mistral-7b",
                "duration_seconds": 2.5
            }
        }


class DLQMessage(BaseModel):
    """Dead Letter Queue 메시지"""
    
    original_topic: str
    original_partition: int
    original_offset: int
    error_message: str
    error_timestamp: datetime = Field(default_factory=datetime.utcnow)
    retry_count: int = 0
    payload: Dict[str, Any]
