"""Stable DTOs for Incident/Runbook Q&A (Plan A)."""

from __future__ import annotations

from typing import List, Optional, Literal, Union

from pydantic import BaseModel, Field


class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags/hints")
    source: Optional[str] = Field(
        default=None,
        description="Optional forcing hint (e.g. 'on_device_rag' or 'cloud_direct')",
    )
    session_id: Optional[str] = Field(default=None, description="Optional session id")


class Citation(BaseModel):
    chunk_id: Union[int, str]
    source: str
    preview: str


class RouteDecision(BaseModel):
    lane: Literal["on_device_rag", "cloud_direct"]
    provider: str
    fallback_used: bool


class Telemetry(BaseModel):
    latency_ms: int
    token_estimate: Optional[int] = None
    char_estimate: Optional[int] = None


class AnswerResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    route: RouteDecision
    telemetry: Telemetry
