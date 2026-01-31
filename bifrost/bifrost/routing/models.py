"""
Data models for Multi-LLM routing system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any


class RoutingStrategy(str, Enum):
    """Routing strategy options."""
    
    # Cost-focused
    COST_OPTIMIZED = "cost_optimized"  # Minimize cost
    
    # Performance-focused
    LATENCY_OPTIMIZED = "latency_optimized"  # Minimize latency
    QUALITY_OPTIMIZED = "quality_optimized"  # Best model quality
    
    # Balanced
    BALANCED = "balanced"  # Balance cost/latency/quality
    
    # Availability-focused
    FAILOVER = "failover"  # Primary with fallback
    ROUND_ROBIN = "round_robin"  # Distribute load evenly
    
    # Smart routing
    ADAPTIVE = "adaptive"  # ML-based adaptive routing


class ProviderType(str, Enum):
    """Supported LLM provider types."""
    
    OLLAMA = "ollama"  # Local on-device
    BEDROCK = "bedrock"  # AWS Bedrock
    OPENAI = "openai"  # OpenAI API
    AZURE_OPENAI = "azure_openai"  # Azure OpenAI
    ANTHROPIC = "anthropic"  # Anthropic Claude
    VERTEX_AI = "vertex_ai"  # Google Vertex AI


@dataclass
class ProviderConfig:
    """
    Configuration for an LLM provider.
    
    Attributes:
        name: Unique provider identifier
        provider_type: Type of provider (ollama, bedrock, etc.)
        model: Model name/ID
        priority: Routing priority (lower = higher priority)
        weight: Load balancing weight
        cost_per_1k_tokens: Cost per 1000 tokens (input + output average)
        avg_latency_ms: Historical average latency
        max_tokens: Maximum context window
        capabilities: List of capabilities (chat, code, embeddings, etc.)
        enabled: Whether provider is enabled
        rate_limit_rpm: Requests per minute limit
        circuit_breaker_name: Associated circuit breaker name
    """
    
    name: str
    provider_type: ProviderType
    model: str
    priority: int = 10
    weight: float = 1.0
    cost_per_1k_tokens: float = 0.0  # Free for local
    avg_latency_ms: float = 1000.0
    max_tokens: int = 4096
    capabilities: List[str] = field(default_factory=lambda: ["chat"])
    enabled: bool = True
    rate_limit_rpm: int = 60
    circuit_breaker_name: Optional[str] = None
    
    # Runtime stats (updated dynamically)
    current_rpm: int = 0
    success_rate: float = 1.0
    last_used: Optional[datetime] = None
    
    def is_available(self) -> bool:
        """Check if provider is available for routing."""
        if not self.enabled:
            return False
        if self.current_rpm >= self.rate_limit_rpm:
            return False
        return True
    
    def effective_score(self, strategy: RoutingStrategy) -> float:
        """
        Calculate effective score for routing decision.
        Lower score = better choice.
        """
        if not self.is_available():
            return float("inf")
        
        if strategy == RoutingStrategy.COST_OPTIMIZED:
            return self.cost_per_1k_tokens
        
        elif strategy == RoutingStrategy.LATENCY_OPTIMIZED:
            return self.avg_latency_ms
        
        elif strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            # Higher priority models have lower priority number
            return self.priority
        
        elif strategy == RoutingStrategy.BALANCED:
            # Weighted combination
            cost_factor = self.cost_per_1k_tokens * 100
            latency_factor = self.avg_latency_ms / 1000
            priority_factor = self.priority
            return (cost_factor + latency_factor + priority_factor) / 3
        
        elif strategy == RoutingStrategy.FAILOVER:
            return self.priority
        
        else:
            return self.priority
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider_type": self.provider_type.value,
            "model": self.model,
            "priority": self.priority,
            "weight": self.weight,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "avg_latency_ms": self.avg_latency_ms,
            "max_tokens": self.max_tokens,
            "capabilities": self.capabilities,
            "enabled": self.enabled,
            "rate_limit_rpm": self.rate_limit_rpm,
            "is_available": self.is_available(),
            "current_rpm": self.current_rpm,
            "success_rate": self.success_rate,
        }


@dataclass
class ProviderHealth:
    """Health status of a provider."""
    
    name: str
    is_healthy: bool
    circuit_state: str = "closed"  # closed, open, half_open
    success_rate: float = 1.0
    avg_latency_ms: float = 0.0
    error_count_1h: int = 0
    last_error: Optional[str] = None
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "is_healthy": self.is_healthy,
            "circuit_state": self.circuit_state,
            "success_rate": round(self.success_rate, 3),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "error_count_1h": self.error_count_1h,
            "last_error": self.last_error,
            "last_check": self.last_check.isoformat(),
        }


@dataclass
class RoutingDecision:
    """
    Result of routing decision.
    
    Contains the selected provider and reasoning.
    """
    
    provider: ProviderConfig
    strategy_used: RoutingStrategy
    score: float
    alternatives: List[str] = field(default_factory=list)
    reason: str = ""
    request_id: Optional[str] = None
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider.name,
            "provider_type": self.provider.provider_type.value,
            "model": self.provider.model,
            "strategy": self.strategy_used.value,
            "score": round(self.score, 4),
            "alternatives": self.alternatives,
            "reason": self.reason,
            "request_id": self.request_id,
            "decided_at": self.decided_at.isoformat(),
        }


@dataclass
class RoutingMetrics:
    """Aggregated routing metrics."""
    
    total_requests: int = 0
    requests_by_provider: Dict[str, int] = field(default_factory=dict)
    requests_by_strategy: Dict[str, int] = field(default_factory=dict)
    avg_routing_time_ms: float = 0.0
    fallback_count: int = 0
    no_provider_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "requests_by_provider": self.requests_by_provider,
            "requests_by_strategy": self.requests_by_strategy,
            "avg_routing_time_ms": round(self.avg_routing_time_ms, 2),
            "fallback_count": self.fallback_count,
            "no_provider_count": self.no_provider_count,
        }
