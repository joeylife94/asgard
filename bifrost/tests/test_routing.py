"""
Tests for Multi-LLM Dynamic Routing System.
"""

import pytest
from unittest.mock import Mock, patch
import time

from bifrost.routing.models import (
    ProviderConfig,
    ProviderType,
    RoutingStrategy,
    RoutingDecision,
    ProviderHealth,
)
from bifrost.routing.cost_optimizer import CostOptimizer, CostBudget, CostEstimate
from bifrost.routing.load_balancer import LoadBalancer
from bifrost.routing.router import DynamicRouter


class TestProviderConfig:
    """Tests for ProviderConfig."""

    def test_provider_creation(self):
        config = ProviderConfig(
            name="test_provider",
            provider_type=ProviderType.OLLAMA,
            model="mistral",
        )
        
        assert config.name == "test_provider"
        assert config.provider_type == ProviderType.OLLAMA
        assert config.model == "mistral"
        assert config.is_available()

    def test_is_available_disabled(self):
        config = ProviderConfig(
            name="disabled",
            provider_type=ProviderType.OLLAMA,
            model="test",
            enabled=False,
        )
        assert not config.is_available()

    def test_is_available_rate_limited(self):
        config = ProviderConfig(
            name="rate_limited",
            provider_type=ProviderType.OLLAMA,
            model="test",
            rate_limit_rpm=10,
            current_rpm=10,  # At limit
        )
        assert not config.is_available()

    def test_effective_score_cost_optimized(self):
        config = ProviderConfig(
            name="test",
            provider_type=ProviderType.BEDROCK,
            model="claude",
            cost_per_1k_tokens=0.002,
        )
        
        score = config.effective_score(RoutingStrategy.COST_OPTIMIZED)
        assert score == 0.002

    def test_effective_score_latency_optimized(self):
        config = ProviderConfig(
            name="test",
            provider_type=ProviderType.OLLAMA,
            model="mistral",
            avg_latency_ms=500,
        )
        
        score = config.effective_score(RoutingStrategy.LATENCY_OPTIMIZED)
        assert score == 500

    def test_to_dict(self):
        config = ProviderConfig(
            name="test",
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            priority=5,
        )
        
        data = config.to_dict()
        assert data["name"] == "test"
        assert data["provider_type"] == "openai"
        assert data["model"] == "gpt-4"


class TestCostOptimizer:
    """Tests for CostOptimizer."""

    def test_estimate_tokens_english(self):
        optimizer = CostOptimizer()
        text = "Hello world, this is a test."  # ~7 words, ~28 chars
        tokens = optimizer.estimate_tokens(text)
        assert 5 <= tokens <= 15

    def test_estimate_tokens_korean(self):
        optimizer = CostOptimizer()
        text = "안녕하세요, 테스트입니다."  # Korean text
        tokens = optimizer.estimate_tokens(text)
        assert tokens > 0

    def test_estimate_tokens_empty(self):
        optimizer = CostOptimizer()
        assert optimizer.estimate_tokens("") == 0

    def test_estimate_cost(self):
        optimizer = CostOptimizer()
        provider = ProviderConfig(
            name="test",
            provider_type=ProviderType.BEDROCK,
            model="claude",
            cost_per_1k_tokens=0.01,
        )
        
        estimate = optimizer.estimate_cost(
            provider,
            "This is a test input",
            expected_output_tokens=100,
        )
        
        assert estimate.provider_name == "test"
        assert estimate.cost_per_1k == 0.01
        assert estimate.estimated_cost > 0

    def test_rank_by_cost(self):
        optimizer = CostOptimizer()
        
        providers = [
            ProviderConfig("expensive", ProviderType.OPENAI, "gpt-4", cost_per_1k_tokens=0.03),
            ProviderConfig("cheap", ProviderType.OLLAMA, "mistral", cost_per_1k_tokens=0.0),
            ProviderConfig("medium", ProviderType.BEDROCK, "claude", cost_per_1k_tokens=0.01),
        ]
        
        ranked = optimizer.rank_by_cost(providers, "test input")
        
        # Cheapest first
        assert ranked[0][0].name == "cheap"
        assert ranked[1][0].name == "medium"
        assert ranked[2][0].name == "expensive"

    def test_budget_tracking(self):
        budget = CostBudget(daily_limit_usd=10.0)
        optimizer = CostOptimizer(budget=budget)
        
        optimizer.record_usage("test", 1000, 0.01)
        
        assert optimizer.budget.daily_spent == 0.01
        assert optimizer.is_within_budget(9.0)
        assert not optimizer.is_within_budget(10.0)

    def test_budget_alert(self):
        budget = CostBudget(daily_limit_usd=10.0, alert_threshold=0.5)
        budget.daily_spent = 6.0  # 60% usage
        
        assert budget.should_alert()


class TestLoadBalancer:
    """Tests for LoadBalancer."""

    def test_select_round_robin(self):
        balancer = LoadBalancer()
        
        providers = [
            ProviderConfig("p1", ProviderType.OLLAMA, "m1"),
            ProviderConfig("p2", ProviderType.OLLAMA, "m2"),
            ProviderConfig("p3", ProviderType.OLLAMA, "m3"),
        ]
        
        # Should cycle through providers
        selected = [balancer.select_round_robin(providers).name for _ in range(6)]
        
        # Each provider should be selected twice
        assert selected.count("p1") == 2
        assert selected.count("p2") == 2
        assert selected.count("p3") == 2

    def test_select_weighted(self):
        balancer = LoadBalancer()
        
        providers = [
            ProviderConfig("high", ProviderType.OLLAMA, "m1", weight=10.0),
            ProviderConfig("low", ProviderType.OLLAMA, "m2", weight=1.0),
        ]
        
        # Run many selections
        counts = {"high": 0, "low": 0}
        for _ in range(1000):
            selected = balancer.select_weighted(providers)
            counts[selected.name] += 1
        
        # High weight should be selected much more often
        assert counts["high"] > counts["low"] * 5

    def test_select_least_connections(self):
        balancer = LoadBalancer()
        
        providers = [
            ProviderConfig("busy", ProviderType.OLLAMA, "m1"),
            ProviderConfig("idle", ProviderType.OLLAMA, "m2"),
        ]
        
        # Simulate busy provider
        balancer._active_requests["busy"] = 5
        balancer._active_requests["idle"] = 0
        
        selected = balancer.select_least_connections(providers)
        assert selected.name == "idle"

    def test_select_fastest(self):
        balancer = LoadBalancer()
        
        providers = [
            ProviderConfig("slow", ProviderType.OLLAMA, "m1", avg_latency_ms=1000),
            ProviderConfig("fast", ProviderType.OLLAMA, "m2", avg_latency_ms=100),
        ]
        
        selected = balancer.select_fastest(providers)
        assert selected.name == "fast"

    def test_request_tracking(self):
        balancer = LoadBalancer()
        
        balancer.record_request_start("provider1")
        assert balancer._active_requests["provider1"] == 1
        
        balancer.record_request_end("provider1", 100.0)
        assert balancer._active_requests["provider1"] == 0
        assert len(balancer._request_times["provider1"]) == 1

    def test_get_stats(self):
        balancer = LoadBalancer()
        
        balancer.record_request_end("p1", 100.0)
        balancer.record_request_end("p1", 200.0)
        
        stats = balancer.get_stats()
        assert "p1" in stats
        assert stats["p1"]["avg_response_time_ms"] == 150.0


class TestDynamicRouter:
    """Tests for DynamicRouter."""

    @pytest.fixture
    def router(self):
        # Reset singleton for testing
        DynamicRouter._instance = None
        router = DynamicRouter()
        # Clear default providers
        router._providers.clear()
        return router

    def test_register_provider(self, router):
        config = ProviderConfig("test", ProviderType.OLLAMA, "mistral")
        router.register_provider(config)
        
        assert "test" in router._providers
        assert router.get_provider("test") is not None

    def test_list_providers(self, router):
        router.register_provider(ProviderConfig("p1", ProviderType.OLLAMA, "m1"))
        router.register_provider(ProviderConfig("p2", ProviderType.BEDROCK, "m2"))
        
        providers = router.list_providers()
        assert len(providers) == 2

    def test_route_cost_optimized(self, router):
        router.register_provider(ProviderConfig(
            "expensive", ProviderType.OPENAI, "gpt-4", cost_per_1k_tokens=0.03
        ))
        router.register_provider(ProviderConfig(
            "cheap", ProviderType.OLLAMA, "mistral", cost_per_1k_tokens=0.0
        ))
        
        decision = router.route("test input", strategy=RoutingStrategy.COST_OPTIMIZED)
        
        assert decision.provider.name == "cheap"
        assert decision.strategy_used == RoutingStrategy.COST_OPTIMIZED

    def test_route_quality_optimized(self, router):
        router.register_provider(ProviderConfig(
            "low_quality", ProviderType.OLLAMA, "m1", priority=10
        ))
        router.register_provider(ProviderConfig(
            "high_quality", ProviderType.BEDROCK, "claude", priority=1
        ))
        
        decision = router.route("test", strategy=RoutingStrategy.QUALITY_OPTIMIZED)
        
        assert decision.provider.name == "high_quality"

    def test_route_with_required_capabilities(self, router):
        router.register_provider(ProviderConfig(
            "basic", ProviderType.OLLAMA, "m1", capabilities=["chat"]
        ))
        router.register_provider(ProviderConfig(
            "advanced", ProviderType.BEDROCK, "m2", capabilities=["chat", "code", "embeddings"]
        ))
        
        decision = router.route(
            "test",
            required_capabilities=["embeddings"]
        )
        
        assert decision.provider.name == "advanced"

    def test_route_with_exclusions(self, router):
        router.register_provider(ProviderConfig("p1", ProviderType.OLLAMA, "m1"))
        router.register_provider(ProviderConfig("p2", ProviderType.OLLAMA, "m2"))
        
        decision = router.route("test", exclude_providers=["p1"])
        
        assert decision.provider.name == "p2"

    def test_record_request_result(self, router):
        router.register_provider(ProviderConfig(
            "test", ProviderType.OLLAMA, "m1", avg_latency_ms=1000
        ))
        
        # Record some fast requests
        for _ in range(10):
            router.record_request_result("test", True, 100.0)
        
        # Latency should be updated (exponential moving average)
        provider = router.get_provider("test")
        assert provider.avg_latency_ms < 1000

    def test_get_provider_health(self, router):
        router.register_provider(ProviderConfig("healthy", ProviderType.OLLAMA, "m1"))
        router.register_provider(ProviderConfig("disabled", ProviderType.OLLAMA, "m2", enabled=False))
        
        health = router.get_provider_health()
        
        assert len(health) == 2
        healthy_provider = next(h for h in health if h.name == "healthy")
        disabled_provider = next(h for h in health if h.name == "disabled")
        
        assert healthy_provider.is_healthy
        assert not disabled_provider.is_healthy

    def test_routing_metrics(self, router):
        router.register_provider(ProviderConfig("p1", ProviderType.OLLAMA, "m1"))
        
        # Make some routing decisions
        for _ in range(5):
            router.route("test")
        
        metrics = router.get_metrics()
        
        assert metrics.total_requests == 5
        assert "p1" in metrics.requests_by_provider


class TestRoutingDecision:
    """Tests for RoutingDecision."""

    def test_to_dict(self):
        provider = ProviderConfig("test", ProviderType.OLLAMA, "mistral")
        decision = RoutingDecision(
            provider=provider,
            strategy_used=RoutingStrategy.BALANCED,
            score=0.5,
            alternatives=["alt1", "alt2"],
            reason="Test reason",
        )
        
        data = decision.to_dict()
        
        assert data["provider_name"] == "test"
        assert data["strategy"] == "balanced"
        assert data["score"] == 0.5
        assert data["alternatives"] == ["alt1", "alt2"]


class TestProviderHealth:
    """Tests for ProviderHealth."""

    def test_to_dict(self):
        health = ProviderHealth(
            name="test",
            is_healthy=True,
            circuit_state="closed",
            success_rate=0.95,
            avg_latency_ms=150.5,
        )
        
        data = health.to_dict()
        
        assert data["name"] == "test"
        assert data["is_healthy"] is True
        assert data["success_rate"] == 0.95
