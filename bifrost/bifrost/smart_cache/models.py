"""
Data models for Smart Caching System.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4


class EvictionStrategy(str, Enum):
    """Cache eviction strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time-based expiration only
    SEMANTIC = "semantic"  # Keep most semantically diverse


class CachePolicy(str, Enum):
    """Cache storage policies."""
    EXACT = "exact"  # Exact query match only
    SEMANTIC = "semantic"  # Semantic similarity matching
    HYBRID = "hybrid"  # Exact match first, then semantic


@dataclass
class CacheConfig:
    """
    Configuration for the smart cache.
    """
    # Size limits
    max_entries: int = 10000
    max_size_mb: int = 500
    
    # TTL settings
    default_ttl_seconds: int = 3600  # 1 hour
    min_ttl_seconds: int = 60  # 1 minute
    max_ttl_seconds: int = 86400  # 24 hours
    
    # Semantic matching
    similarity_threshold: float = 0.85  # 0.0 - 1.0
    enable_semantic_cache: bool = True
    
    # Eviction
    eviction_strategy: EvictionStrategy = EvictionStrategy.LRU
    eviction_batch_size: int = 100
    
    # Policy
    cache_policy: CachePolicy = CachePolicy.HYBRID
    
    # Performance
    enable_compression: bool = True
    enable_analytics: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_entries": self.max_entries,
            "max_size_mb": self.max_size_mb,
            "default_ttl_seconds": self.default_ttl_seconds,
            "min_ttl_seconds": self.min_ttl_seconds,
            "max_ttl_seconds": self.max_ttl_seconds,
            "similarity_threshold": self.similarity_threshold,
            "enable_semantic_cache": self.enable_semantic_cache,
            "eviction_strategy": self.eviction_strategy.value,
            "cache_policy": self.cache_policy.value,
            "enable_compression": self.enable_compression,
            "enable_analytics": self.enable_analytics,
        }


@dataclass
class CacheEntry:
    """
    A cached response entry.
    """
    id: UUID = field(default_factory=uuid4)
    
    # Query/Response
    query: str = ""
    query_hash: str = ""  # For exact matching
    query_embedding: Optional[List[float]] = None  # For semantic matching
    
    response: str = ""
    response_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Source info
    provider: Optional[str] = None
    model: Optional[str] = None
    lane: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    accessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    # Usage stats
    hit_count: int = 0
    quality_score: Optional[float] = None
    
    # Compression
    is_compressed: bool = False
    original_size: int = 0
    compressed_size: int = 0
    
    def is_expired(self, now: Optional[datetime] = None) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        now = now or datetime.now(timezone.utc)
        return now >= self.expires_at
    
    def touch(self) -> None:
        """Update access time and hit count."""
        self.accessed_at = datetime.now(timezone.utc)
        self.hit_count += 1
    
    @property
    def ttl_remaining(self) -> Optional[int]:
        """Get remaining TTL in seconds."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, int(delta.total_seconds()))
    
    @property
    def age_seconds(self) -> int:
        """Get entry age in seconds."""
        delta = datetime.now(timezone.utc) - self.created_at
        return int(delta.total_seconds())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "query": self.query,
            "query_hash": self.query_hash,
            "response": self.response,
            "provider": self.provider,
            "model": self.model,
            "lane": self.lane,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "hit_count": self.hit_count,
            "quality_score": self.quality_score,
            "ttl_remaining": self.ttl_remaining,
            "age_seconds": self.age_seconds,
        }


@dataclass
class CacheStats:
    """
    Cache statistics and analytics.
    """
    # Size
    total_entries: int = 0
    total_size_bytes: int = 0
    avg_entry_size_bytes: int = 0
    
    # Hit rates
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    exact_hits: int = 0
    semantic_hits: int = 0
    
    # Performance
    avg_lookup_time_ms: float = 0.0
    avg_semantic_match_time_ms: float = 0.0
    
    # TTL
    expired_count: int = 0
    evicted_count: int = 0
    
    # Quality
    avg_quality_score: Optional[float] = None
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
    
    @property
    def exact_hit_rate(self) -> float:
        """Calculate exact match hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.exact_hits / self.total_requests
    
    @property
    def semantic_hit_rate(self) -> float:
        """Calculate semantic match hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.semantic_hits / self.total_requests
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_entries": self.total_entries,
            "total_size_bytes": self.total_size_bytes,
            "total_size_mb": round(self.total_size_bytes / (1024 * 1024), 2),
            "avg_entry_size_bytes": self.avg_entry_size_bytes,
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": round(self.hit_rate, 4),
            "exact_hits": self.exact_hits,
            "exact_hit_rate": round(self.exact_hit_rate, 4),
            "semantic_hits": self.semantic_hits,
            "semantic_hit_rate": round(self.semantic_hit_rate, 4),
            "avg_lookup_time_ms": round(self.avg_lookup_time_ms, 3),
            "expired_count": self.expired_count,
            "evicted_count": self.evicted_count,
            "avg_quality_score": round(self.avg_quality_score, 3) if self.avg_quality_score else None,
        }


@dataclass
class CacheLookupResult:
    """
    Result of a cache lookup operation.
    """
    hit: bool = False
    entry: Optional[CacheEntry] = None
    match_type: Optional[str] = None  # "exact", "semantic"
    similarity_score: Optional[float] = None
    lookup_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hit": self.hit,
            "match_type": self.match_type,
            "similarity_score": self.similarity_score,
            "lookup_time_ms": round(self.lookup_time_ms, 3),
            "entry": self.entry.to_dict() if self.entry else None,
        }
