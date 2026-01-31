"""
Cost Optimizer for Multi-LLM routing.

Estimates and optimizes costs across different LLM providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import threading

from bifrost.routing.models import ProviderConfig, ProviderType
from bifrost.logger import logger


# Cost estimates per 1K tokens (approximate, varies by model)
DEFAULT_COSTS = {
    ProviderType.OLLAMA: 0.0,  # Local, free (electricity cost only)
    ProviderType.BEDROCK: 0.002,  # ~$0.002 for Claude Haiku
    ProviderType.OPENAI: 0.01,  # ~$0.01 for GPT-3.5-turbo
    ProviderType.AZURE_OPENAI: 0.01,
    ProviderType.ANTHROPIC: 0.008,  # ~$0.008 for Claude 3 Haiku
    ProviderType.VERTEX_AI: 0.005,
}


@dataclass
class CostEstimate:
    """Cost estimate for a request."""
    
    provider_name: str
    estimated_tokens: int
    cost_per_1k: float
    estimated_cost: float
    currency: str = "USD"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "estimated_tokens": self.estimated_tokens,
            "cost_per_1k": self.cost_per_1k,
            "estimated_cost": round(self.estimated_cost, 6),
            "currency": self.currency,
        }


@dataclass
class CostBudget:
    """Cost budget configuration."""
    
    daily_limit_usd: float = 10.0
    monthly_limit_usd: float = 100.0
    alert_threshold: float = 0.8  # Alert at 80% usage
    
    daily_spent: float = 0.0
    monthly_spent: float = 0.0
    last_reset_daily: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_reset_monthly: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_within_budget(self, additional_cost: float = 0) -> bool:
        """Check if additional cost is within budget."""
        if self.daily_spent + additional_cost > self.daily_limit_usd:
            return False
        if self.monthly_spent + additional_cost > self.monthly_limit_usd:
            return False
        return True
    
    def should_alert(self) -> bool:
        """Check if usage is above alert threshold."""
        daily_usage = self.daily_spent / self.daily_limit_usd if self.daily_limit_usd > 0 else 0
        monthly_usage = self.monthly_spent / self.monthly_limit_usd if self.monthly_limit_usd > 0 else 0
        return daily_usage >= self.alert_threshold or monthly_usage >= self.alert_threshold
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "daily_limit_usd": self.daily_limit_usd,
            "monthly_limit_usd": self.monthly_limit_usd,
            "daily_spent": round(self.daily_spent, 4),
            "monthly_spent": round(self.monthly_spent, 4),
            "daily_remaining": round(self.daily_limit_usd - self.daily_spent, 4),
            "monthly_remaining": round(self.monthly_limit_usd - self.monthly_spent, 4),
            "daily_usage_percent": round(self.daily_spent / self.daily_limit_usd * 100, 1) if self.daily_limit_usd > 0 else 0,
            "monthly_usage_percent": round(self.monthly_spent / self.monthly_limit_usd * 100, 1) if self.monthly_limit_usd > 0 else 0,
        }


class CostOptimizer:
    """
    Cost optimizer for LLM provider selection.
    
    Features:
    - Token estimation from text
    - Cost calculation per provider
    - Budget tracking and enforcement
    - Cost-based provider ranking
    """
    
    def __init__(
        self,
        budget: Optional[CostBudget] = None,
        custom_costs: Optional[Dict[str, float]] = None,
    ):
        self.budget = budget or CostBudget()
        self.custom_costs = custom_costs or {}
        self._lock = threading.Lock()
        
        # Cost tracking
        self._request_costs: List[Dict[str, Any]] = []
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text.
        
        Uses a simple heuristic: ~4 characters per token for English,
        ~2 characters per token for CJK (Korean, Japanese, Chinese).
        """
        if not text:
            return 0
        
        # Count CJK characters
        cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\uac00' <= c <= '\ud7a3' or '\u3040' <= c <= '\u30ff')
        non_cjk_count = len(text) - cjk_count
        
        # Estimate tokens
        cjk_tokens = cjk_count / 1.5  # ~1.5 chars per token for CJK
        non_cjk_tokens = non_cjk_count / 4  # ~4 chars per token for English
        
        return int(cjk_tokens + non_cjk_tokens)
    
    def get_cost_per_1k(self, provider: ProviderConfig) -> float:
        """Get cost per 1K tokens for a provider."""
        # Check custom costs first
        if provider.name in self.custom_costs:
            return self.custom_costs[provider.name]
        
        # Use provider's configured cost
        if provider.cost_per_1k_tokens > 0:
            return provider.cost_per_1k_tokens
        
        # Fall back to defaults
        return DEFAULT_COSTS.get(provider.provider_type, 0.01)
    
    def estimate_cost(
        self,
        provider: ProviderConfig,
        input_text: str,
        expected_output_tokens: int = 500,
    ) -> CostEstimate:
        """
        Estimate cost for a request.
        
        Args:
            provider: Target provider
            input_text: Input text/prompt
            expected_output_tokens: Expected output token count
        """
        input_tokens = self.estimate_tokens(input_text)
        total_tokens = input_tokens + expected_output_tokens
        cost_per_1k = self.get_cost_per_1k(provider)
        estimated_cost = (total_tokens / 1000) * cost_per_1k
        
        return CostEstimate(
            provider_name=provider.name,
            estimated_tokens=total_tokens,
            cost_per_1k=cost_per_1k,
            estimated_cost=estimated_cost,
        )
    
    def rank_by_cost(
        self,
        providers: List[ProviderConfig],
        input_text: str,
        expected_output_tokens: int = 500,
    ) -> List[tuple[ProviderConfig, CostEstimate]]:
        """
        Rank providers by estimated cost (lowest first).
        
        Returns list of (provider, cost_estimate) tuples.
        """
        estimates = []
        for provider in providers:
            if not provider.is_available():
                continue
            estimate = self.estimate_cost(provider, input_text, expected_output_tokens)
            estimates.append((provider, estimate))
        
        # Sort by cost (lowest first)
        estimates.sort(key=lambda x: x[1].estimated_cost)
        return estimates
    
    def record_usage(
        self,
        provider_name: str,
        actual_tokens: int,
        actual_cost: float,
    ) -> None:
        """Record actual usage for budget tracking."""
        with self._lock:
            now = datetime.now(timezone.utc)
            
            # Reset daily budget if new day
            if now.date() > self.budget.last_reset_daily.date():
                self.budget.daily_spent = 0.0
                self.budget.last_reset_daily = now
            
            # Reset monthly budget if new month
            if now.month != self.budget.last_reset_monthly.month or now.year != self.budget.last_reset_monthly.year:
                self.budget.monthly_spent = 0.0
                self.budget.last_reset_monthly = now
            
            # Update spent
            self.budget.daily_spent += actual_cost
            self.budget.monthly_spent += actual_cost
            
            # Track request
            self._request_costs.append({
                "provider": provider_name,
                "tokens": actual_tokens,
                "cost": actual_cost,
                "timestamp": now.isoformat(),
            })
            
            # Keep only last 1000 requests
            if len(self._request_costs) > 1000:
                self._request_costs = self._request_costs[-1000:]
            
            # Log if approaching budget
            if self.budget.should_alert():
                logger.warning(
                    "cost_budget_alert",
                    daily_spent=self.budget.daily_spent,
                    daily_limit=self.budget.daily_limit_usd,
                    monthly_spent=self.budget.monthly_spent,
                    monthly_limit=self.budget.monthly_limit_usd,
                )
    
    def is_within_budget(self, estimated_cost: float) -> bool:
        """Check if estimated cost is within budget."""
        return self.budget.is_within_budget(estimated_cost)
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status."""
        return self.budget.to_dict()
    
    def get_cost_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get cost summary for time period."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        with self._lock:
            recent = [
                r for r in self._request_costs
                if datetime.fromisoformat(r["timestamp"]) >= cutoff
            ]
        
        total_cost = sum(r["cost"] for r in recent)
        total_tokens = sum(r["tokens"] for r in recent)
        
        by_provider: Dict[str, Dict[str, Any]] = {}
        for r in recent:
            provider = r["provider"]
            if provider not in by_provider:
                by_provider[provider] = {"cost": 0.0, "tokens": 0, "requests": 0}
            by_provider[provider]["cost"] += r["cost"]
            by_provider[provider]["tokens"] += r["tokens"]
            by_provider[provider]["requests"] += 1
        
        return {
            "period_hours": hours,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "request_count": len(recent),
            "by_provider": {
                k: {
                    "cost": round(v["cost"], 4),
                    "tokens": v["tokens"],
                    "requests": v["requests"],
                }
                for k, v in by_provider.items()
            },
            "budget_status": self.get_budget_status(),
        }
