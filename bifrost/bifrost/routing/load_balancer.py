"""
Load Balancer for Multi-LLM routing.

Distributes requests across providers using various algorithms.
"""

from __future__ import annotations

import random
import threading
import time
from datetime import datetime, timezone
from typing import Optional, List, Dict

from bifrost.routing.models import ProviderConfig
from bifrost.logger import logger


class LoadBalancer:
    """
    Load balancer for distributing requests across LLM providers.
    
    Supports multiple algorithms:
    - Round Robin: Equal distribution
    - Weighted: Based on provider weights
    - Least Connections: Route to least busy provider
    - Random: Random selection
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._round_robin_index = 0
        self._active_requests: Dict[str, int] = {}  # provider_name -> active count
        self._request_times: Dict[str, List[float]] = {}  # provider_name -> recent response times
    
    def select_round_robin(self, providers: List[ProviderConfig]) -> Optional[ProviderConfig]:
        """
        Select provider using round robin.
        
        Simple rotation through available providers.
        """
        available = [p for p in providers if p.is_available()]
        if not available:
            return None
        
        with self._lock:
            self._round_robin_index = (self._round_robin_index + 1) % len(available)
            return available[self._round_robin_index]
    
    def select_weighted(self, providers: List[ProviderConfig]) -> Optional[ProviderConfig]:
        """
        Select provider using weighted random.
        
        Providers with higher weights get more traffic.
        """
        available = [p for p in providers if p.is_available()]
        if not available:
            return None
        
        total_weight = sum(p.weight for p in available)
        if total_weight == 0:
            return random.choice(available)
        
        r = random.uniform(0, total_weight)
        cumulative = 0.0
        
        for provider in available:
            cumulative += provider.weight
            if r <= cumulative:
                return provider
        
        return available[-1]
    
    def select_least_connections(self, providers: List[ProviderConfig]) -> Optional[ProviderConfig]:
        """
        Select provider with least active connections.
        
        Routes to the least busy provider.
        """
        available = [p for p in providers if p.is_available()]
        if not available:
            return None
        
        with self._lock:
            # Find provider with least active requests
            min_active = float("inf")
            selected = available[0]
            
            for provider in available:
                active = self._active_requests.get(provider.name, 0)
                if active < min_active:
                    min_active = active
                    selected = provider
            
            return selected
    
    def select_random(self, providers: List[ProviderConfig]) -> Optional[ProviderConfig]:
        """
        Select provider randomly.
        """
        available = [p for p in providers if p.is_available()]
        if not available:
            return None
        return random.choice(available)
    
    def select_fastest(self, providers: List[ProviderConfig]) -> Optional[ProviderConfig]:
        """
        Select provider with best recent response times.
        """
        available = [p for p in providers if p.is_available()]
        if not available:
            return None
        
        with self._lock:
            # Calculate average response time for each provider
            avg_times: Dict[str, float] = {}
            for provider in available:
                times = self._request_times.get(provider.name, [])
                if times:
                    avg_times[provider.name] = sum(times) / len(times)
                else:
                    # Use configured average if no recent data
                    avg_times[provider.name] = provider.avg_latency_ms
        
        # Select provider with lowest average response time
        selected = min(available, key=lambda p: avg_times.get(p.name, float("inf")))
        return selected
    
    def record_request_start(self, provider_name: str) -> None:
        """Record that a request has started."""
        with self._lock:
            self._active_requests[provider_name] = self._active_requests.get(provider_name, 0) + 1
    
    def record_request_end(
        self,
        provider_name: str,
        response_time_ms: float,
        success: bool = True,
    ) -> None:
        """
        Record that a request has ended.
        
        Updates active count and response time tracking.
        """
        with self._lock:
            # Decrease active count
            if provider_name in self._active_requests:
                self._active_requests[provider_name] = max(
                    0, self._active_requests[provider_name] - 1
                )
            
            # Track response time (keep last 100)
            if provider_name not in self._request_times:
                self._request_times[provider_name] = []
            
            self._request_times[provider_name].append(response_time_ms)
            if len(self._request_times[provider_name]) > 100:
                self._request_times[provider_name] = self._request_times[provider_name][-100:]
    
    def get_stats(self) -> Dict[str, Dict[str, any]]:
        """Get load balancer statistics."""
        with self._lock:
            stats = {}
            for name in set(list(self._active_requests.keys()) + list(self._request_times.keys())):
                times = self._request_times.get(name, [])
                stats[name] = {
                    "active_requests": self._active_requests.get(name, 0),
                    "recent_requests": len(times),
                    "avg_response_time_ms": round(sum(times) / len(times), 1) if times else 0,
                    "min_response_time_ms": round(min(times), 1) if times else 0,
                    "max_response_time_ms": round(max(times), 1) if times else 0,
                }
            return stats
    
    def reset_stats(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self._active_requests.clear()
            self._request_times.clear()
            self._round_robin_index = 0
