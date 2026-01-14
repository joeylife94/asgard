"""Lane answerers (no direct FastAPI coupling)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from bifrost.contracts.ask import Citation
from bifrost.on_device.rag.context_builder import ContextBuilder
from bifrost.on_device.rag.retriever import RagRetriever
from bifrost.providers.on_device.ollama_provider import OllamaProvider
from bifrost.providers.cloud.bedrock_provider import BedrockProvider


@dataclass(frozen=True)
class AnswerAttempt:
    answer: str
    citations: List[Citation]
    provider: str
    token_estimate: Optional[int]
    char_estimate: int


class OnDeviceRagAnswerer:
    def __init__(self):
        self.retriever = RagRetriever()
        self.builder = ContextBuilder()
        self.provider = OllamaProvider()

    def answer(self, question: str, top_k: int = 5) -> AnswerAttempt:
        chunks = self.retriever.retrieve(question, top_k=top_k)
        built = self.builder.build(question, chunks)
        result = self.provider.generate(built.prompt)
        return AnswerAttempt(
            answer=result.text,
            citations=built.citations,
            provider=result.provider,
            token_estimate=result.token_estimate,
            char_estimate=built.char_estimate,
        )


class CloudDirectAnswerer:
    def __init__(self):
        self.provider = BedrockProvider()

    def answer(self, question: str) -> AnswerAttempt:
        # Cloud lane MUST NOT use RAG
        prompt = (
            "You are an incident assistant. Provide a safe, operational answer. "
            "If unsure, say so.\n\n"
            f"QUESTION:\n{question.strip()}\n"
        )
        result = self.provider.generate(prompt)
        return AnswerAttempt(
            answer=result.text,
            citations=[],
            provider=result.provider,
            token_estimate=result.token_estimate,
            char_estimate=len(prompt),
        )
