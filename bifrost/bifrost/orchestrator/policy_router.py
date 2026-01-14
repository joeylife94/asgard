"""Policy router for lane selection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Literal


Lane = Literal["on_device_rag", "cloud_direct"]


@dataclass(frozen=True)
class PolicyDecision:
    lane: Lane
    provider: str


class PolicyRouter:
    def __init__(self):
        self.enable_cloud = os.getenv("ENABLE_CLOUD_LANE", "false").lower() in ("true", "1", "yes")
        self.cloud_provider = os.getenv("BIFROST_CLOUD_PROVIDER", "bedrock").lower()
        self.on_device_provider = os.getenv("BIFROST_ON_DEVICE_PROVIDER", "ollama").lower()

    def decide(self, *, question: str, source_hint: Optional[str] = None) -> PolicyDecision:
        # Default: on-device RAG always
        if source_hint and source_hint.lower() in ("cloud", "cloud_direct"):
            if self.enable_cloud:
                return PolicyDecision(lane="cloud_direct", provider=self.cloud_provider)
            # cloud requested but disabled: stay on-device

        return PolicyDecision(lane="on_device_rag", provider=self.on_device_provider)
