"""On-device lane answerer (RAG).

RAG modules must live under `bifrost/on_device/rag/` and are only imported here.
"""

from __future__ import annotations

import os
from typing import Optional

from bifrost.on_device.rag.context_builder import ContextBuilder
from bifrost.on_device.rag.retriever import RagRetriever
from bifrost.providers.on_device.ollama_provider import OllamaProvider

from .types import AnswerAttempt


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


class OnDeviceRagAnswerer:
    def __init__(self):
        self.top_k = _get_int_env("BIFROST_RAG_TOP_K", 5)
        self.retriever = RagRetriever()
        self.builder = ContextBuilder()
        self.provider = OllamaProvider()

    def answer(self, question: str, top_k: Optional[int] = None) -> AnswerAttempt:
        k = top_k if top_k is not None else self.top_k
        chunks = self.retriever.retrieve(question, top_k=k)
        built = self.builder.build(question, chunks)
        result = self.provider.generate(built.prompt)
        return AnswerAttempt(
            answer=result.text,
            citations=built.citations,
            provider=result.provider,
            token_estimate=result.token_estimate,
            char_estimate=built.char_estimate,
        )
