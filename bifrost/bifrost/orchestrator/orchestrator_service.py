"""OrchestratorService: /ask entrypoint (no direct provider calls from API)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Tuple

import anyio

from bifrost.contracts.ask import AnswerRequest, AnswerResponse, RouteDecision, Telemetry
from bifrost.logger import logger

from .policy_router import PolicyRouter
from .answerers import OnDeviceRagAnswerer, CloudDirectAnswerer, AnswerAttempt


@dataclass(frozen=True)
class OrchestratorConfig:
    timeout_seconds: float = 12.0
    max_retries: int = 1


def _looks_low_confidence(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return True
    if len(t) < 60:
        return True
    markers = ["i don't know", "not sure", "can't", "cannot", "unknown"]
    return any(m in t for m in markers)


class OrchestratorService:
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
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

            if _looks_low_confidence(attempt.answer) and decision.lane == "on_device_rag":
                # deterministic fallback for low-confidence
                fallback_used = True
                outcome = "fallback"
                attempt = self._fallback_from_rag(question=req.question)
                retrieved_ids = [c.chunk_id for c in attempt.citations]

        except Exception as e:
            fallback_used = True
            outcome = "error"
            if decision.lane == "on_device_rag":
                attempt = self._fallback_from_rag(question=req.question)
                retrieved_ids = [c.chunk_id for c in attempt.citations]
            else:
                attempt = AnswerAttempt(
                    answer="I can't confidently answer right now.",
                    citations=[],
                    provider=decision.provider,
                    token_estimate=None,
                    char_estimate=0,
                )
                retrieved_ids = []

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
        chunks = self.on_device.retriever.retrieve(question, top_k=5)
        built = self.on_device.builder.build(question, chunks)
        ids = [c.chunk_id for c in built.citations]
        answer = (
            "I can't confidently answer based on available runbooks.\n\n"
            "Closest runbook snippets:\n"
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
