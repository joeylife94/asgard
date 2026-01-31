"""
Dynamic Router for Multi-LLM routing.

Main entry point for intelligent LLM provider selection.
"""

from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from bifrost.routing.models import (
    ProviderConfig,
    ProviderType,
    ProviderHealth,
    RoutingStrategy,
    RoutingDecision,
    RoutingMetrics,
)
from bifrost.routing.cost_optimizer import CostOptimizer, CostBudget
from bifrost.routing.load_balancer import LoadBalancer
from bifrost.resilience import circuit_breaker_registry, CircuitState
from bifrost.logger import logger


class DynamicRouter:
    """
    Dynamic LLM router with intelligent provider selection.
    
    Features:
    - Multiple routing strategies (cost, latency, quality, balanced)
    - Circuit breaker integration for availability
    - Cost optimization and budget enforcement
    - Load balancing across providers
    - Automatic failover
    """
    
    _instance: Optional["DynamicRouter"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "DynamicRouter":
        """Singleton pattern."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._providers: Dict[str, ProviderConfig] = {}
        self._default_strategy = RoutingStrategy(
            os.getenv("BIFROST_ROUTING_STRATEGY", "balanced")
        )
        
        # Initialize components
        budget = CostBudget(
            daily_limit_usd=float(os.getenv("BIFROST_DAILY_COST_LIMIT", "10.0")),
            monthly_limit_usd=float(os.getenv("BIFROST_MONTHLY_COST_LIMIT", "100.0")),
        )
        self._cost_optimizer = CostOptimizer(budget=budget)
        self._load_balancer = LoadBalancer()
        
        # Metrics tracking
        self._metrics = RoutingMetrics()
        self._metrics_lock = threading.Lock()
        
        # Initialize default providers
        self._init_default_providers()
        
        self._initialized = True
        logger.info("dynamic_router_initialized", strategy=self._default_strategy.value)
    
    def _init_default_providers(self) -> None:
        """Initialize default provider configurations."""
        
        # On-device Ollama (local, free, lower latency for local)
        self.register_provider(ProviderConfig(
            name="ollama_local",
            provider_type=ProviderType.OLLAMA,
            model=os.getenv("OLLAMA_MODEL", "mistral"),
            priority=1,
            weight=2.0,
            cost_per_1k_tokens=0.0,
            avg_latency_ms=500,
            max_tokens=4096,
            capabilities=["chat", "code", "analysis"],
            circuit_breaker_name="on_device_rag",
        ))
        
        # AWS Bedrock (cloud, paid, high quality)
        if os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"):
            self.register_provider(ProviderConfig(
                name="bedrock_claude",
                provider_type=ProviderType.BEDROCK,
                model=os.getenv("BEDROCK_MODEL", "anthropic.claude-3-haiku-20240307-v1:0"),
                priority=5,
                weight=1.0,
                cost_per_1k_tokens=0.002,
                avg_latency_ms=1500,
                max_tokens=200000,
                capabilities=["chat", "code", "analysis", "long_context"],
                circuit_breaker_name="cloud_direct",
            ))
    
    def register_provider(self, config: ProviderConfig) -> None:
        """Register a new provider configuration."""
        self._providers[config.name] = config
        logger.info(
            "provider_registered",
            name=config.name,
            provider_type=config.provider_type.value,
            model=config.model,
        )
    
    def unregister_provider(self, name: str) -> None:
        """Remove a provider from the registry."""
        if name in self._providers:
            del self._providers[name]
            logger.info("provider_unregistered", name=name)
    
    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """Get a specific provider configuration."""
        return self._providers.get(name)
    
    def list_providers(self) -> List[ProviderConfig]:
        """List all registered providers."""
        return list(self._providers.values())
    
    def route(
        self,
        input_text: str,
        strategy: Optional[RoutingStrategy] = None,
        required_capabilities: Optional[List[str]] = None,
        exclude_providers: Optional[List[str]] = None,
        request_id: Optional[str] = None,
    ) -> RoutingDecision:
        """
        Route a request to the best available provider.
        
        Args:
            input_text: The input text/prompt
            strategy: Routing strategy (uses default if not specified)
            required_capabilities: Required provider capabilities
            exclude_providers: Providers to exclude
            request_id: Request ID for tracking
        
        Returns:
            RoutingDecision with selected provider and reasoning
        """
        start_time = time.time()
        strategy = strategy or self._default_strategy
        
        # Filter available providers
        candidates = self._filter_providers(
            required_capabilities=required_capabilities,
            exclude_providers=exclude_providers,
        )
        
        if not candidates:
            logger.warning(
                "no_providers_available",
                required_capabilities=required_capabilities,
                exclude_providers=exclude_providers,
            )
            # Return fallback (first provider even if unavailable)
            fallback = list(self._providers.values())[0] if self._providers else None
            if fallback:
                return RoutingDecision(
                    provider=fallback,
                    strategy_used=strategy,
                    score=float("inf"),
                    reason="No available providers, using fallback",
                    request_id=request_id,
                )
            raise RuntimeError("No LLM providers configured")
        
        # Select provider based on strategy
        decision = self._select_provider(candidates, input_text, strategy, request_id)
        
        # Track metrics
        routing_time_ms = (time.time() - start_time) * 1000
        self._record_routing(decision, routing_time_ms)
        
        logger.info(
            "routing_decision",
            provider=decision.provider.name,
            strategy=strategy.value,
            score=decision.score,
            candidates=len(candidates),
            routing_time_ms=routing_time_ms,
            request_id=request_id,
        )
        
        return decision
    
    def _filter_providers(
        self,
        required_capabilities: Optional[List[str]] = None,
        exclude_providers: Optional[List[str]] = None,
    ) -> List[ProviderConfig]:
        """Filter providers based on requirements."""
        candidates = []
        
        for provider in self._providers.values():
            # Check exclusion
            if exclude_providers and provider.name in exclude_providers:
                continue
            
            # Check enabled
            if not provider.enabled:
                continue
            
            # Check capabilities
            if required_capabilities:
                if not all(cap in provider.capabilities for cap in required_capabilities):
                    continue
            
            # Check circuit breaker
            if provider.circuit_breaker_name:
                try:
                    cb = circuit_breaker_registry.get(provider.circuit_breaker_name)
                    if cb.state == CircuitState.OPEN:
                        continue
                except:
                    pass
            
            # Check rate limit
            if not provider.is_available():
                continue
            
            candidates.append(provider)
        
        return candidates
    
    def _select_provider(
        self,
        candidates: List[ProviderConfig],
        input_text: str,
        strategy: RoutingStrategy,
        request_id: Optional[str],
    ) -> RoutingDecision:
        """Select the best provider based on strategy."""
        
        if strategy == RoutingStrategy.COST_OPTIMIZED:
            return self._select_by_cost(candidates, input_text, request_id)
        
        elif strategy == RoutingStrategy.LATENCY_OPTIMIZED:
            return self._select_by_latency(candidates, request_id)
        
        elif strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            return self._select_by_quality(candidates, request_id)
        
        elif strategy == RoutingStrategy.ROUND_ROBIN:
            provider = self._load_balancer.select_round_robin(candidates)
            return RoutingDecision(
                provider=provider or candidates[0],
                strategy_used=strategy,
                score=0,
                alternatives=[p.name for p in candidates if p != provider][:3],
                reason="Round robin selection",
                request_id=request_id,
            )
        
        elif strategy == RoutingStrategy.FAILOVER:
            return self._select_failover(candidates, request_id)
        
        else:  # BALANCED or ADAPTIVE
            return self._select_balanced(candidates, input_text, request_id)
    
    def _select_by_cost(
        self,
        candidates: List[ProviderConfig],
        input_text: str,
        request_id: Optional[str],
    ) -> RoutingDecision:
        """Select cheapest provider."""
        ranked = self._cost_optimizer.rank_by_cost(candidates, input_text)
        
        if not ranked:
            return RoutingDecision(
                provider=candidates[0],
                strategy_used=RoutingStrategy.COST_OPTIMIZED,
                score=float("inf"),
                reason="No cost data available",
                request_id=request_id,
            )
        
        provider, estimate = ranked[0]
        return RoutingDecision(
            provider=provider,
            strategy_used=RoutingStrategy.COST_OPTIMIZED,
            score=estimate.estimated_cost,
            alternatives=[p.name for p, _ in ranked[1:4]],
            reason=f"Lowest cost: ${estimate.estimated_cost:.6f}",
            request_id=request_id,
        )
    
    def _select_by_latency(
        self,
        candidates: List[ProviderConfig],
        request_id: Optional[str],
    ) -> RoutingDecision:
        """Select fastest provider."""
        provider = self._load_balancer.select_fastest(candidates)
        
        if not provider:
            provider = candidates[0]
        
        return RoutingDecision(
            provider=provider,
            strategy_used=RoutingStrategy.LATENCY_OPTIMIZED,
            score=provider.avg_latency_ms,
            alternatives=[p.name for p in candidates if p != provider][:3],
            reason=f"Lowest latency: {provider.avg_latency_ms}ms",
            request_id=request_id,
        )
    
    def _select_by_quality(
        self,
        candidates: List[ProviderConfig],
        request_id: Optional[str],
    ) -> RoutingDecision:
        """Select highest quality provider."""
        sorted_candidates = sorted(candidates, key=lambda p: p.priority)
        provider = sorted_candidates[0]
        
        return RoutingDecision(
            provider=provider,
            strategy_used=RoutingStrategy.QUALITY_OPTIMIZED,
            score=provider.priority,
            alternatives=[p.name for p in sorted_candidates[1:4]],
            reason=f"Highest quality (priority {provider.priority})",
            request_id=request_id,
        )
    
    def _select_failover(
        self,
        candidates: List[ProviderConfig],
        request_id: Optional[str],
    ) -> RoutingDecision:
        """Select primary with failover list."""
        sorted_candidates = sorted(candidates, key=lambda p: p.priority)
        provider = sorted_candidates[0]
        
        return RoutingDecision(
            provider=provider,
            strategy_used=RoutingStrategy.FAILOVER,
            score=provider.priority,
            alternatives=[p.name for p in sorted_candidates[1:]],
            reason=f"Primary: {provider.name}, failovers: {len(sorted_candidates) - 1}",
            request_id=request_id,
        )
    
    def _select_balanced(
        self,
        candidates: List[ProviderConfig],
        input_text: str,
        request_id: Optional[str],
    ) -> RoutingDecision:
        """Balanced selection considering cost, latency, and quality."""
        scores: Dict[str, float] = {}
        
        for provider in candidates:
            # Cost factor (0-1, lower is better)
            cost = self._cost_optimizer.get_cost_per_1k(provider)
            max_cost = max(self._cost_optimizer.get_cost_per_1k(p) for p in candidates) or 1
            cost_score = cost / max_cost if max_cost > 0 else 0
            
            # Latency factor (0-1, lower is better)
            max_latency = max(p.avg_latency_ms for p in candidates) or 1
            latency_score = provider.avg_latency_ms / max_latency
            
            # Quality factor (0-1, lower priority number is better)
            max_priority = max(p.priority for p in candidates) or 1
            quality_score = provider.priority / max_priority
            
            # Combined score (weighted average)
            scores[provider.name] = (
                cost_score * 0.3 +
                latency_score * 0.3 +
                quality_score * 0.4
            )
        
        # Select provider with lowest combined score
        best = min(candidates, key=lambda p: scores.get(p.name, float("inf")))
        
        sorted_by_score = sorted(candidates, key=lambda p: scores.get(p.name, float("inf")))
        
        return RoutingDecision(
            provider=best,
            strategy_used=RoutingStrategy.BALANCED,
            score=scores.get(best.name, 0),
            alternatives=[p.name for p in sorted_by_score[1:4]],
            reason=f"Balanced score: {scores.get(best.name, 0):.3f}",
            request_id=request_id,
        )
    
    def _record_routing(self, decision: RoutingDecision, routing_time_ms: float) -> None:
        """Record routing metrics."""
        with self._metrics_lock:
            self._metrics.total_requests += 1
            
            provider = decision.provider.name
            self._metrics.requests_by_provider[provider] = (
                self._metrics.requests_by_provider.get(provider, 0) + 1
            )
            
            strategy = decision.strategy_used.value
            self._metrics.requests_by_strategy[strategy] = (
                self._metrics.requests_by_strategy.get(strategy, 0) + 1
            )
            
            # Running average
            n = self._metrics.total_requests
            self._metrics.avg_routing_time_ms = (
                (self._metrics.avg_routing_time_ms * (n - 1) + routing_time_ms) / n
            )
    
    def record_request_result(
        self,
        provider_name: str,
        success: bool,
        latency_ms: float,
        tokens_used: int = 0,
        cost: float = 0.0,
    ) -> None:
        """
        Record the result of a request for adaptive routing.
        
        Should be called after each LLM request completes.
        """
        # Update load balancer stats
        self._load_balancer.record_request_end(provider_name, latency_ms, success)
        
        # Update cost tracking
        if cost > 0:
            self._cost_optimizer.record_usage(provider_name, tokens_used, cost)
        
        # Update provider stats
        if provider_name in self._providers:
            provider = self._providers[provider_name]
            # Update success rate (exponential moving average)
            alpha = 0.1
            success_val = 1.0 if success else 0.0
            provider.success_rate = alpha * success_val + (1 - alpha) * provider.success_rate
            
            # Update latency (exponential moving average)
            provider.avg_latency_ms = alpha * latency_ms + (1 - alpha) * provider.avg_latency_ms
            provider.last_used = datetime.now(timezone.utc)
    
    def get_provider_health(self) -> List[ProviderHealth]:
        """Get health status of all providers."""
        health_list = []
        
        for provider in self._providers.values():
            # Check circuit breaker state
            circuit_state = "closed"
            if provider.circuit_breaker_name:
                try:
                    cb = circuit_breaker_registry.get(provider.circuit_breaker_name)
                    circuit_state = cb.state.value
                except:
                    pass
            
            health = ProviderHealth(
                name=provider.name,
                is_healthy=provider.is_available() and circuit_state != "open",
                circuit_state=circuit_state,
                success_rate=provider.success_rate,
                avg_latency_ms=provider.avg_latency_ms,
            )
            health_list.append(health)
        
        return health_list
    
    def get_metrics(self) -> RoutingMetrics:
        """Get routing metrics."""
        return self._metrics
    
    def get_cost_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get cost summary."""
        return self._cost_optimizer.get_cost_summary(hours)
    
    def set_default_strategy(self, strategy: RoutingStrategy) -> None:
        """Set the default routing strategy."""
        self._default_strategy = strategy
        logger.info("routing_strategy_changed", strategy=strategy.value)


# Global router getter
def get_dynamic_router() -> DynamicRouter:
    """Get the singleton dynamic router instance."""
    return DynamicRouter()
