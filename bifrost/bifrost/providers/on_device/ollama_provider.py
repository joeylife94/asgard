"""Ollama wrapper (on-device lane).

Supports a deterministic stub mode for interview demos/tests.
"""

from __future__ import annotations

import os
from typing import Optional

from bifrost.config import Config
from bifrost.ollama import OllamaClient

from .base import OnDeviceLlmProvider, LlmResult


class OllamaProvider(OnDeviceLlmProvider):
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()

        self.mode = os.getenv("BIFROST_ON_DEVICE_MODE", "ollama").lower()
        self.stub_answer = os.getenv(
            "BIFROST_ON_DEVICE_STUB_ANSWER",
            "(stub) 로컬 LLM이 비활성화되어 요약 답변을 반환했습니다.",
        )

        if self.mode != "ollama":
            self.client = None
            return

        url = self.config.get("ollama.url")
        model = self.config.get("ollama.model")
        timeout = int(self.config.get("ollama.timeout", 120))
        max_retries = int(self.config.get("ollama.max_retries", 3))
        self.client = OllamaClient(url=url, model=model, timeout=timeout, max_retries=max_retries)

    def generate(self, prompt: str) -> LlmResult:
        if self.mode != "ollama" or self.client is None:
            return LlmResult(text=self.stub_answer, provider="on_device_stub", token_estimate=None)

        result = self.client.analyze(prompt, stream=False)
        text = result.get("response", "")
        return LlmResult(text=text, provider="ollama", token_estimate=None)
