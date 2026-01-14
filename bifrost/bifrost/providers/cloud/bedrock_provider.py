"""AWS Bedrock wrapper (cloud lane)."""

from __future__ import annotations

from typing import Optional

from bifrost.config import Config
from bifrost.bedrock import BedrockClient, is_bedrock_available

from .base import CloudLlmProvider, LlmResult


class BedrockProvider(CloudLlmProvider):
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()

        if not is_bedrock_available():
            raise RuntimeError("Bedrock provider not available (boto3 not installed)")

        region = self.config.get("bedrock.region")
        model_id = self.config.get("bedrock.model")
        profile = self.config.get("bedrock.profile")
        self.client = BedrockClient(region=region, model_id=model_id, profile=profile)

    def generate(self, prompt: str) -> LlmResult:
        result = self.client.analyze(prompt)
        text = result.get("response", "")
        usage = (result.get("metadata") or {}).get("usage") or {}
        token_estimate = usage.get("output_tokens") or usage.get("tokens")
        return LlmResult(text=text, provider="bedrock", token_estimate=token_estimate)
