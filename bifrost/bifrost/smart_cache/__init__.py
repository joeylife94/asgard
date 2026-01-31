"""
Smart Caching System for Bifrost.

Provides intelligent caching with semantic similarity matching,
TTL management, and cache analytics.
"""

from bifrost.smart_cache.models import (
    CacheEntry,
    CacheConfig,
    CacheStats,
    CachePolicy,
    EvictionStrategy,
)
from bifrost.smart_cache.semantic import SemanticMatcher
from bifrost.smart_cache.cache_manager import SmartCacheManager, get_cache_manager

__all__ = [
    "CacheEntry",
    "CacheConfig",
    "CacheStats",
    "CachePolicy",
    "EvictionStrategy",
    "SemanticMatcher",
    "SmartCacheManager",
    "get_cache_manager",
]
