"""Kafka Event Schema - Heimdall <-> Bifrost control-plane events.

Kafka is the primary control plane:
- analysis.request starts jobs
- analysis.result completes jobs
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


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
    """Heimdall -> Bifrost. Topic: analysis.request"""

    model_config = ConfigDict(populate_by_name=True)

    schema_version: int = Field(default=1)
    job_id: str = Field(..., description="Job UUID")
    idempotency_key: str = Field(..., description="Deduplication key")
    log_id: int = Field(..., description="Heimdall log id")
    tenant_id: Optional[str] = None
    priority: Optional[str] = None
    timeout_ms: Optional[int] = None
    model_policy: Optional[Dict[str, Any]] = None
    trace_id: str = Field(..., description="Trace id (propagated)")

    # Minimal backward compatibility
    request_id: Optional[str] = Field(default=None, description="Legacy alias", repr=False)
    correlation_id: Optional[str] = Field(default=None, description="Legacy alias", repr=False)

    def normalized_job_id(self) -> str:
        return self.job_id or self.request_id  # type: ignore[return-value]

    def normalized_trace_id(self) -> str:
        return self.trace_id or self.correlation_id  # type: ignore[return-value]


class TokenUsage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class AnalysisResultEvent(BaseModel):
    """Bifrost -> Heimdall. Topic: analysis.result"""

    model_config = ConfigDict(populate_by_name=True)

    schema_version: int = Field(default=1)
    job_id: str
    status: str

    summary: Optional[str] = None
    root_cause: Optional[str] = None
    recommendation: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[Decimal] = None

    model_used: Optional[str] = None
    token_usage: Optional[TokenUsage] = None
    latency_ms: Optional[int] = None

    error_code: Optional[str] = None
    error_message: Optional[str] = None
    trace_id: str
    log_id: Optional[int] = None


class DlqFailedEvent(BaseModel):
    """Bifrost -> Heimdall. Topic: dlq.failed (processing failure signal)."""

    model_config = ConfigDict(populate_by_name=True)

    schema_version: int = Field(default=1)
    job_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    error_code: Optional[str] = None
    error_message: str
    trace_id: Optional[str] = None

    original_topic: str
    original_partition: int
    original_offset: int
    failed_at: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]
