"""
Tests for Circuit Breaker pattern implementation.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch

from bifrost.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitBreakerRegistry,
    CircuitState,
    get_circuit_breaker,
)


class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig."""

    def test_default_config(self):
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.recovery_timeout == 30.0
        assert config.name == "default"

    def test_for_llm_provider(self):
        config = CircuitBreakerConfig.for_llm_provider("ollama")
        assert config.failure_threshold == 3
        assert config.success_threshold == 2
        assert config.recovery_timeout == 60.0
        assert config.name == "ollama"

    def test_for_external_api(self):
        config = CircuitBreakerConfig.for_external_api("bedrock")
        assert config.failure_threshold == 5
        assert config.success_threshold == 3
        assert config.recovery_timeout == 30.0
        assert config.name == "bedrock"


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    def test_initial_state_is_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_closed
        assert not cb.is_open
        assert not cb.is_half_open

    def test_successful_call(self):
        cb = CircuitBreaker()
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.stats.successful_calls == 1
        assert cb.stats.failed_calls == 0

    def test_failed_call_increments_counter(self):
        cb = CircuitBreaker()
        
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("test error")))
        
        assert cb.stats.failed_calls == 1
        assert cb.stats.consecutive_failures == 1

    def test_circuit_opens_after_threshold(self):
        config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=1.0)
        cb = CircuitBreaker(config)

        # Trigger 3 failures
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        assert cb.state == CircuitState.OPEN
        assert cb.is_open

    def test_open_circuit_rejects_calls(self):
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=10.0)
        cb = CircuitBreaker(config)

        # Trip the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        assert cb.is_open

        # Next call should be rejected
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            cb.call(lambda: "should not execute")

        assert cb.stats.rejected_calls == 1
        assert "OPEN" in str(exc_info.value)

    def test_circuit_transitions_to_half_open_after_timeout(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1,  # 100ms
        )
        cb = CircuitBreaker(config)

        # Trip the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        assert cb.is_open

        # Wait for recovery timeout
        time.sleep(0.15)

        # State should transition to HALF_OPEN when checked
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.is_half_open

    def test_half_open_closes_on_success_threshold(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            recovery_timeout=0.1,
        )
        cb = CircuitBreaker(config)

        # Trip the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        # Wait for recovery
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN

        # Successful calls in HALF_OPEN
        cb.call(lambda: "success1")
        assert cb.is_half_open  # Still half-open after 1 success

        cb.call(lambda: "success2")
        assert cb.is_closed  # Closed after 2 successes

    def test_half_open_opens_on_failure(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1,
        )
        cb = CircuitBreaker(config)

        # Trip the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        # Wait for recovery
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN

        # Failure in HALF_OPEN immediately opens
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        assert cb.is_open

    def test_manual_reset(self):
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(config)

        # Trip the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        assert cb.is_open

        # Manual reset
        cb.reset()
        assert cb.is_closed
        assert cb.stats.consecutive_failures == 0

    def test_excluded_exceptions_not_counted(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            excluded_exceptions=(KeyError,),
        )
        cb = CircuitBreaker(config)

        # KeyError should not count
        for _ in range(5):
            with pytest.raises(KeyError):
                cb.call(lambda: (_ for _ in ()).throw(KeyError("not counted")))

        assert cb.is_closed  # Still closed
        assert cb.stats.failed_calls == 0  # Not counted as failures

    def test_decorator_sync(self):
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(config)

        @cb
        def my_function(x):
            return x * 2

        result = my_function(5)
        assert result == 10
        assert cb.stats.successful_calls == 1

    def test_context_manager(self):
        cb = CircuitBreaker()

        with cb:
            result = "operation"

        assert cb.stats.successful_calls == 1

    def test_context_manager_failure(self):
        cb = CircuitBreaker()

        with pytest.raises(RuntimeError):
            with cb:
                raise RuntimeError("test error")

        assert cb.stats.failed_calls == 1

    def test_stats_tracking(self):
        cb = CircuitBreaker()

        # Success
        cb.call(lambda: "ok")

        # Failures
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        stats = cb.stats.to_dict()
        assert stats["total_calls"] == 2
        assert stats["successful_calls"] == 1
        assert stats["failed_calls"] == 1
        assert stats["last_success_time"] is not None
        assert stats["last_failure_time"] is not None


class TestCircuitBreakerRegistry:
    """Tests for CircuitBreakerRegistry."""

    def test_singleton(self):
        registry1 = CircuitBreakerRegistry()
        registry2 = CircuitBreakerRegistry()
        assert registry1 is registry2

    def test_get_or_create(self):
        registry = CircuitBreakerRegistry()
        
        # Clear any existing breakers for test isolation
        registry._breakers = {}

        cb1 = registry.get("test_service")
        cb2 = registry.get("test_service")

        assert cb1 is cb2
        assert cb1.config.name == "test_service"

    def test_get_with_config(self):
        registry = CircuitBreakerRegistry()
        registry._breakers = {}

        config = CircuitBreakerConfig.for_llm_provider("custom")
        cb = registry.get("custom_service", config)

        assert cb.config.failure_threshold == 3
        assert cb.config.name == "custom_service"

    def test_get_all_stats(self):
        registry = CircuitBreakerRegistry()
        registry._breakers = {}

        registry.get("service_a")
        registry.get("service_b")

        stats = registry.get_all_stats()
        assert "service_a" in stats
        assert "service_b" in stats
        assert stats["service_a"]["state"] == "closed"

    def test_reset_all(self):
        registry = CircuitBreakerRegistry()
        registry._breakers = {}

        cb1 = registry.get("svc1", CircuitBreakerConfig(failure_threshold=1))
        cb2 = registry.get("svc2", CircuitBreakerConfig(failure_threshold=1))

        # Trip both circuits
        with pytest.raises(ValueError):
            cb1.call(lambda: (_ for _ in ()).throw(ValueError("error")))
        with pytest.raises(ValueError):
            cb2.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        assert cb1.is_open
        assert cb2.is_open

        registry.reset_all()

        assert cb1.is_closed
        assert cb2.is_closed

    def test_remove(self):
        registry = CircuitBreakerRegistry()
        registry._breakers = {}

        registry.get("to_remove")
        assert "to_remove" in registry._breakers

        registry.remove("to_remove")
        assert "to_remove" not in registry._breakers


class TestGetCircuitBreaker:
    """Tests for the convenience function."""

    def test_get_circuit_breaker_function(self):
        # Reset registry for test isolation
        CircuitBreakerRegistry._instance = None

        cb = get_circuit_breaker("my_service")
        assert cb.config.name == "my_service"

        cb2 = get_circuit_breaker("my_service")
        assert cb is cb2


class TestCircuitBreakerThreadSafety:
    """Tests for thread safety."""

    def test_concurrent_calls(self):
        config = CircuitBreakerConfig(failure_threshold=100)  # High threshold
        cb = CircuitBreaker(config)
        errors = []
        success_count = [0]
        lock = threading.Lock()

        def worker():
            for _ in range(100):
                try:
                    cb.call(lambda: "ok")
                    with lock:
                        success_count[0] += 1
                except Exception as e:
                    with lock:
                        errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert success_count[0] == 1000
        assert cb.stats.successful_calls == 1000


@pytest.mark.asyncio
class TestCircuitBreakerAsync:
    """Tests for async functionality."""

    async def test_async_call_success(self):
        cb = CircuitBreaker()

        async def async_operation():
            return "async result"

        result = await cb.call_async(async_operation)
        assert result == "async result"
        assert cb.stats.successful_calls == 1

    async def test_async_call_failure(self):
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(config)

        async def async_failing():
            raise RuntimeError("async error")

        # Trigger failures
        with pytest.raises(RuntimeError):
            await cb.call_async(async_failing)
        with pytest.raises(RuntimeError):
            await cb.call_async(async_failing)

        assert cb.is_open

    async def test_async_decorator(self):
        cb = CircuitBreaker()

        @cb
        async def async_decorated(x):
            return x + 1

        result = await async_decorated(5)
        assert result == 6
        assert cb.stats.successful_calls == 1
