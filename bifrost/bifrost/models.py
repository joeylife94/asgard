"""데이터베이스 모델"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, 
    Boolean, JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def utcnow() -> datetime:
    """UTC now as naive datetime (UTC)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AnalysisResult(Base):
    """로그 분석 결과"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 메타데이터
    created_at = Column(DateTime, default=utcnow, nullable=False, index=True)
    source = Column(String(50), nullable=False)  # "local" or "cloud"
    model = Column(String(100), nullable=False, index=True)
    
    # 입력
    log_content = Column(Text, nullable=False)
    log_hash = Column(String(64), nullable=False, index=True)  # SHA256
    log_size_bytes = Column(Integer, nullable=False)
    log_lines = Column(Integer, nullable=False)
    
    # 프롬프트
    prompt_template = Column(String(50), default="master")
    prompt_version = Column(String(20), default="1.0")
    
    # 출력
    response = Column(Text, nullable=False)
    response_size_bytes = Column(Integer, nullable=False)
    
    # 성능 메트릭
    duration_seconds = Column(Float, nullable=False)
    tokens_used = Column(Integer, nullable=True)  # Bedrock only
    
    # 설정
    config = Column(JSON, nullable=True)  # 사용된 설정 스냅샷
    
    # 태그 & 분류
    tags = Column(JSON, default=list)  # ["k8s", "error", "critical"]
    service_name = Column(String(100), nullable=True, index=True)
    environment = Column(String(50), nullable=True)  # "prod", "staging", etc.
    
    # 상태
    status = Column(String(20), default="completed")  # completed, failed, processing
    error_message = Column(Text, nullable=True)
    
    # 관계
    metrics = relationship("AnalysisMetric", back_populates="analysis", cascade="all, delete-orphan")
    
    # 인덱스
    __table_args__ = (
        Index('idx_created_service', 'created_at', 'service_name'),
        Index('idx_model_status', 'model', 'status'),
    )
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source": self.source,
            "model": self.model,
            "log_hash": self.log_hash,
            "log_size_bytes": self.log_size_bytes,
            "log_lines": self.log_lines,
            "response": self.response,
            "duration_seconds": self.duration_seconds,
            "tokens_used": self.tokens_used,
            "tags": self.tags,
            "service_name": self.service_name,
            "environment": self.environment,
            "status": self.status,
        }


class AnalysisMetric(Base):
    """분석 메트릭 (시계열)"""
    __tablename__ = "analysis_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)
    
    timestamp = Column(DateTime, default=utcnow, nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)
    
    # 관계
    analysis = relationship("AnalysisResult", back_populates="metrics")
    
    __table_args__ = (
        Index('idx_metric_time', 'metric_name', 'timestamp'),
    )


class PromptTemplate(Base):
    """프롬프트 템플릿 관리"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    version = Column(String(20), nullable=False)
    
    template = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # 메타데이터
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    # A/B 테스팅
    usage_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    avg_duration = Column(Float, default=0.0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "template": self.template,
            "description": self.description,
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "avg_duration": self.avg_duration,
        }


class APIKey(Base):
    """API 키 관리"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    
    # 권한
    is_active = Column(Boolean, default=True, index=True)
    rate_limit_per_hour = Column(Integer, default=100)
    
    # 사용 통계
    created_at = Column(DateTime, default=utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # 메타
    description = Column(Text, nullable=True)
    owner = Column(String(100), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "key": self.key[:8] + "..." + self.key[-4:],  # 마스킹
            "is_active": self.is_active,
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "usage_count": self.usage_count,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }


class RunbookChunk(Base):
    """Runbook/doc chunk for on-device RAG."""

    __tablename__ = "runbook_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=utcnow, nullable=False, index=True)

    source = Column(String(255), nullable=False, index=True)
    tags = Column(JSON, default=list)
    content = Column(Text, nullable=False)

    __table_args__ = (
        Index('idx_runbook_source_created', 'source', 'created_at'),
    )
