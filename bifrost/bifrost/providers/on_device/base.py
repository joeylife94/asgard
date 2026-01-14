"""On-device provider interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional


@dataclass(frozen=True)
class LlmResult:
    text: str
    provider: str
    token_estimate: Optional[int] = None


class OnDeviceLlmProvider(Protocol):
    def generate(self, prompt: str) -> LlmResult:
        ...
