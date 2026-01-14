"""Cloud lane answerer (direct).

IMPORTANT: This module must NOT import any RAG modules.
"""

from __future__ import annotations

from bifrost.providers.cloud.bedrock_provider import BedrockProvider

from .types import AnswerAttempt


class CloudDirectAnswerer:
    def __init__(self):
        self.provider = BedrockProvider()

    def answer(self, question: str) -> AnswerAttempt:
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
