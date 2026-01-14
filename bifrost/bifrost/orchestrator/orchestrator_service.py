"""OrchestratorService: /ask entrypoint (no direct provider calls from API)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

import anyio

from bifrost.contracts.ask import AnswerRequest, AnswerResponse, RouteDecision, Telemetry
from bifrost.logger import logger

from .policy_router import PolicyRouter
from .answerers.on_device import OnDeviceRagAnswerer
from .answerers.cloud import CloudDirectAnswerer
from .answerers.types import AnswerAttempt


@dataclass(frozen=True)
class OrchestratorConfig:
    timeout_seconds: float = 12.0
    max_retries: int = 1

    @classmethod
    def from_env(cls) -> "OrchestratorConfig":
        timeout_seconds = _get_float_env("BIFROST_LLM_TIMEOUT_SECONDS", 12.0)
        max_retries = _get_int_env("BIFROST_LLM_MAX_RETRIES", 1)
        return cls(timeout_seconds=timeout_seconds, max_retries=max_retries)


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value >= 0 else default


def _get_float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _looks_low_confidence(text: str) -> bool:
    # Deterministic heuristic policy (interview-friendly):
    # - Empty/very short answer => low confidence
    # - Contains uncertainty markers (EN + KR) => low confidence
    t = (text or "").strip().lower()
    if not t:
        return True
    if len(t) < 60:
        return True
    markers = [
        "i don't know",
        "not sure",
        "can't",
        "cannot",
        "unknown",
        # Korean uncertainty markers (substring match)
        "모르",
        "확신",
        "알 수 없",
        "불확실",
    ]
    return any(m in t for m in markers)


class OrchestratorService:
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig.from_env()
        self.router = PolicyRouter()
        self.on_device = OnDeviceRagAnswerer()
        self.cloud = None  # lazy init

    async def ask(self, req: AnswerRequest, request_id: str) -> AnswerResponse:
        start = time.time()
        decision = self.router.decide(question=req.question, source_hint=req.source)

        logger.info(
            "ask_start",
            request_id=request_id,
            lane=decision.lane,
            provider=decision.provider,
        )

        outcome = "ok"
        fallback_used = False
        attempt: Optional[AnswerAttempt] = None

        try:
            attempt = await self._call_with_timeout_and_retry(decision.lane, req.question)
            if decision.lane == "on_device_rag":
                retrieved_ids = [c.chunk_id for c in attempt.citations]
            else:
                retrieved_ids = []

            low_confidence = _looks_low_confidence(attempt.answer)
            # On-device RAG must produce citations; lack of citations implies we could not ground the answer.
            if decision.lane == "on_device_rag" and not attempt.citations:
                low_confidence = True

            if low_confidence:
                # deterministic fallback for low-confidence (always uses on-device RAG snippets)
                fallback_used = True
                outcome = "fallback"
                attempt = self._fallback_from_rag(question=req.question)
                retrieved_ids = [c.chunk_id for c in attempt.citations]

        except Exception as e:
            fallback_used = True
            outcome = "error"
            # Deterministic fallback always uses on-device RAG snippets (RAG stays on-device lane)
            attempt = self._fallback_from_rag(question=req.question)
            retrieved_ids = [c.chunk_id for c in attempt.citations]

            logger.error(
                "ask_error",
                request_id=request_id,
                lane=decision.lane,
                provider=decision.provider,
                error=str(e),
            )

        latency_ms = int((time.time() - start) * 1000)

        logger.info(
            "ask_end",
            request_id=request_id,
            lane=decision.lane,
            provider=attempt.provider if attempt else decision.provider,
            retrieved_chunk_ids=retrieved_ids,
            latency_ms=latency_ms,
            outcome=outcome,
            fallback_used=fallback_used,
        )

        return AnswerResponse(
            answer=attempt.answer if attempt else "",
            citations=attempt.citations if attempt else [],
            route=RouteDecision(
                lane=decision.lane,
                provider=attempt.provider if attempt else decision.provider,
                fallback_used=fallback_used,
            ),
            telemetry=Telemetry(
                latency_ms=latency_ms,
                token_estimate=attempt.token_estimate if attempt else None,
                char_estimate=attempt.char_estimate if attempt else None,
            ),
        )

    async def _call_with_timeout_and_retry(self, lane: str, question: str) -> AnswerAttempt:
        last_exc: Optional[BaseException] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                with anyio.fail_after(self.config.timeout_seconds):
                    return await anyio.to_thread.run_sync(self._sync_answer, lane, question)
            except BaseException as e:
                last_exc = e
                if attempt >= self.config.max_retries:
                    break

        raise RuntimeError(f"LLM call failed after retries: {last_exc}")

    def _sync_answer(self, lane: str, question: str) -> AnswerAttempt:
        if lane == "cloud_direct":
            if self.cloud is None:
                self.cloud = CloudDirectAnswerer()
            return self.cloud.answer(question)
        return self.on_device.answer(question)

    def _fallback_from_rag(self, question: str) -> AnswerAttempt:
        # Build a deterministic answer containing the best snippets
        chunks = self.on_device.retriever.retrieve(question, top_k=self.on_device.top_k)
        built = self.on_device.builder.build(question, chunks)
        answer = (
            "I can't confidently answer based on the runbook evidence.\n"
            "현재 런북 근거만으로는 확신 있게 답변하기 어렵습니다.\n\n"
            "가장 관련 있어 보이는 런북 스니펫:\n"
        )
        for c in built.citations:
            answer += f"- [chunk:{c.chunk_id} source:{c.source}] {c.preview}\n"
        return AnswerAttempt(
            answer=answer,
            citations=built.citations,
            provider="fallback",
            token_estimate=None,
            char_estimate=built.char_estimate,
        )
