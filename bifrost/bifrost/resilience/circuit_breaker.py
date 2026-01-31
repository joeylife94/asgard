"""
Circuit Breaker Pattern Implementation for Bifrost.

Provides fault tolerance for external service calls (LLM providers, etc.)
with configurable failure thresholds, recovery timeouts, and half-open states.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Circuit tripped, requests fail fast
- HALF_OPEN: Testing recovery, limited requests allowed
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, TypeVar, Optional, Dict, Any
from functools import wraps

from bifrost.logger import logger


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    
    # Failure threshold to trip the circuit
    failure_threshold: int = 5
    
    # Success threshold to close circuit from half-open
    success_threshold: int = 2
    
    # Time in seconds before attempting recovery (open -> half-open)
    recovery_timeout: float = 30.0
    
    # Exceptions that should count as failures
    # If None, all exceptions count as failures
    expected_exceptions: tuple = (Exception,)
    
    # Exceptions to exclude from failure count (e.g., validation errors)
    excluded_exceptions: tuple = ()
    
    # Name for logging/metrics
    name: str = "default"

    @classmethod
    def for_llm_provider(cls, name: str = "llm") -> "CircuitBreakerConfig":
        """Preset config for LLM provider calls."""
        return cls(
            failure_threshold=3,
            success_threshold=2,
            recovery_timeout=60.0,
            name=name,
        )

    @classmethod
    def for_external_api(cls, name: str = "api") -> "CircuitBreakerConfig":
        """Preset config for external API calls."""
        return cls(
            failure_threshold=5,
            success_threshold=3,
            recovery_timeout=30.0,
            name=name,
        )


@dataclass
class CircuitBreakerStats:
    """Statistics for monitoring circuit breaker behavior."""
    
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0  # Calls rejected due to open circuit
    state_transitions: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "state_transitions": self.state_transitions,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit is open and call is rejected."""
    
    def __init__(self, name: str, recovery_time: float):
        self.name = name
        self.recovery_time = recovery_time
        super().__init__(
            f"Circuit breaker '{name}' is OPEN. "
            f"Recovery in {recovery_time:.1f}s"
        )


class CircuitBreaker:
    """
    Thread-safe Circuit Breaker implementation.
    
    Usage:
        cb = CircuitBreaker(CircuitBreakerConfig.for_llm_provider("ollama"))
        
        # As decorator
        @cb
        def call_ollama():
            ...
        
        # As context manager
        with cb:
            call_ollama()
        
        # Direct call
        result = cb.call(call_ollama)
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._stats = CircuitBreakerStats()
        self._last_state_change = time.time()
        self._lock = threading.RLock()
    
    @property
    def state(self) -> CircuitState:
        """Current circuit state (may transition to HALF_OPEN if timeout elapsed)."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state
    
    @property
    def stats(self) -> CircuitBreakerStats:
        """Current statistics."""
        return self._stats
    
    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        return self.state == CircuitState.HALF_OPEN
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        elapsed = time.time() - self._last_state_change
        return elapsed >= self.config.recovery_timeout
    
    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state with logging."""
        old_state = self._state
        if old_state == new_state:
            return
        
        self._state = new_state
        self._last_state_change = time.time()
        self._stats.state_transitions += 1
        
        logger.info(
            "circuit_breaker_transition",
            name=self.config.name,
            from_state=old_state.value,
            to_state=new_state.value,
            consecutive_failures=self._stats.consecutive_failures,
            consecutive_successes=self._stats.consecutive_successes,
        )
    
    def _record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            self._stats.total_calls += 1
            self._stats.successful_calls += 1
            self._stats.consecutive_successes += 1
            self._stats.consecutive_failures = 0
            self._stats.last_success_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                if self._stats.consecutive_successes >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
    
    def _record_failure(self, exc: Exception) -> None:
        """Record a failed call."""
        with self._lock:
            self._stats.total_calls += 1
            self._stats.failed_calls += 1
            self._stats.consecutive_failures += 1
            self._stats.consecutive_successes = 0
            self._stats.last_failure_time = time.time()
            
            logger.warning(
                "circuit_breaker_failure",
                name=self.config.name,
                state=self._state.value,
                consecutive_failures=self._stats.consecutive_failures,
                error=str(exc),
            )
            
            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens the circuit
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._stats.consecutive_failures >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)
    
    def _should_count_as_failure(self, exc: Exception) -> bool:
        """Check if exception should count as a failure."""
        # Excluded exceptions never count
        if isinstance(exc, self.config.excluded_exceptions):
            return False
        # Check if it matches expected exceptions
        return isinstance(exc, self.config.expected_exceptions)
    
    def _check_state(self) -> None:
        """Check if call is allowed, raise if circuit is open."""
        current_state = self.state  # This may trigger OPEN -> HALF_OPEN
        
        if current_state == CircuitState.OPEN:
            self._stats.rejected_calls += 1
            remaining = self.config.recovery_timeout - (time.time() - self._last_state_change)
            raise CircuitBreakerOpenError(self.config.name, max(0, remaining))
    
    def call(self, func: Callable[[], T]) -> T:
        """Execute a function with circuit breaker protection."""
        self._check_state()
        
        try:
            result = func()
            self._record_success()
            return result
        except Exception as e:
            if self._should_count_as_failure(e):
                self._record_failure(e)
            raise
    
    async def call_async(self, func: Callable[[], T]) -> T:
        """Execute an async function with circuit breaker protection."""
        self._check_state()
        
        try:
            result = await func()
            self._record_success()
            return result
        except Exception as e:
            if self._should_count_as_failure(e):
                self._record_failure(e)
            raise
    
    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)
            self._stats.consecutive_failures = 0
            self._stats.consecutive_successes = 0
            logger.info("circuit_breaker_reset", name=self.config.name)
    
    def __call__(self, func: Callable) -> Callable:
        """Use as a decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(lambda: func(*args, **kwargs))
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self.call_async(lambda: func(*args, **kwargs))
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    def __enter__(self):
        """Use as a context manager."""
        self._check_state()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Record result when exiting context."""
        if exc_val is None:
            self._record_success()
        elif self._should_count_as_failure(exc_val):
            self._record_failure(exc_val)
        return False  # Don't suppress exceptions


T = TypeVar("T")


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.
    
    Usage:
        registry = CircuitBreakerRegistry()
        
        # Get or create circuit breaker
        cb = registry.get("ollama", CircuitBreakerConfig.for_llm_provider("ollama"))
        
        # Get all stats
        all_stats = registry.get_all_stats()
    """
    
    _instance: Optional["CircuitBreakerRegistry"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "CircuitBreakerRegistry":
        """Singleton pattern."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._breakers: Dict[str, CircuitBreaker] = {}
                cls._instance._registry_lock = threading.Lock()
            return cls._instance
    
    def get(
        self, 
        name: str, 
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create a circuit breaker by name."""
        with self._registry_lock:
            if name not in self._breakers:
                if config is None:
                    config = CircuitBreakerConfig(name=name)
                else:
                    config.name = name
                self._breakers[name] = CircuitBreaker(config)
            return self._breakers[name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all registered circuit breakers."""
        with self._registry_lock:
            return {
                name: {
                    "state": cb.state.value,
                    "stats": cb.stats.to_dict(),
                }
                for name, cb in self._breakers.items()
            }
    
    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        with self._registry_lock:
            for cb in self._breakers.values():
                cb.reset()
    
    def remove(self, name: str) -> None:
        """Remove a circuit breaker from the registry."""
        with self._registry_lock:
            self._breakers.pop(name, None)


# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """Convenience function to get a circuit breaker from the global registry."""
    return circuit_breaker_registry.get(name, config)
