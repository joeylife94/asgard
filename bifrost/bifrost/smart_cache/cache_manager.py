"""
Smart Cache Manager - Intelligent caching with semantic matching.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import zlib
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator
from uuid import UUID

from bifrost.smart_cache.models import (
    CacheEntry,
    CacheConfig,
    CacheStats,
    CachePolicy,
    EvictionStrategy,
    CacheLookupResult,
)
from bifrost.smart_cache.semantic import SemanticMatcher
from bifrost.logger import logger


class SmartCacheManager:
    """
    Intelligent cache manager with semantic similarity matching.
    
    Features:
    - Exact query matching
    - Semantic similarity matching
    - TTL-based expiration
    - Multiple eviction strategies
    - Compression support
    - Analytics tracking
    """
    
    _instance: Optional["SmartCacheManager"] = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: Optional[str] = None, config: Optional[CacheConfig] = None) -> "SmartCacheManager":
        """Singleton pattern."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_path: Optional[str] = None, config: Optional[CacheConfig] = None):
        if self._initialized:
            return
        
        self._db_path = db_path or str(Path.home() / ".bifrost" / "smart_cache.db")
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.config = config or CacheConfig()
        self.matcher = SemanticMatcher(threshold=self.config.similarity_threshold)
        
        self._local = threading.local()
        self._init_db()
        
        # In-memory stats
        self._stats = CacheStats()
        self._stats_lock = threading.Lock()
        
        self._initialized = True
        
        logger.info("smart_cache_initialized", db_path=self._db_path)
    
    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get thread-local database connection."""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self._db_path,
                check_same_thread=False,
                timeout=30.0,
            )
            self._local.connection.row_factory = sqlite3.Row
        
        try:
            yield self._local.connection
        except Exception:
            self._local.connection.rollback()
            raise
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    query_hash TEXT NOT NULL,
                    response BLOB NOT NULL,
                    response_metadata TEXT,
                    provider TEXT,
                    model TEXT,
                    lane TEXT,
                    created_at TEXT NOT NULL,
                    accessed_at TEXT NOT NULL,
                    expires_at TEXT,
                    hit_count INTEGER DEFAULT 0,
                    quality_score REAL,
                    is_compressed INTEGER DEFAULT 0,
                    original_size INTEGER DEFAULT 0,
                    compressed_size INTEGER DEFAULT 0
                );
                
                CREATE INDEX IF NOT EXISTS idx_cache_hash 
                    ON cache_entries(query_hash);
                CREATE INDEX IF NOT EXISTS idx_cache_expires 
                    ON cache_entries(expires_at);
                CREATE INDEX IF NOT EXISTS idx_cache_accessed 
                    ON cache_entries(accessed_at);
            """)
            conn.commit()
    
    # ==================== Core Operations ====================
    
    def get(
        self,
        query: str,
        use_semantic: Optional[bool] = None,
    ) -> CacheLookupResult:
        """
        Look up a query in the cache.
        
        Args:
            query: The query to look up
            use_semantic: Override config for semantic matching
        """
        start_time = time.time()
        
        # Track request
        with self._stats_lock:
            self._stats.total_requests += 1
        
        # Try exact match first
        query_hash = self.matcher.get_hash(query)
        entry = self._get_by_hash(query_hash)
        
        if entry and not entry.is_expired():
            entry.touch()
            self._update_access(entry)
            
            lookup_time = (time.time() - start_time) * 1000
            self._update_stats(hit=True, exact=True, lookup_time=lookup_time)
            
            return CacheLookupResult(
                hit=True,
                entry=entry,
                match_type="exact",
                similarity_score=1.0,
                lookup_time_ms=lookup_time,
            )
        
        # Try semantic match if enabled
        enable_semantic = use_semantic if use_semantic is not None else self.config.enable_semantic_cache
        
        if enable_semantic and self.config.cache_policy != CachePolicy.EXACT:
            result = self._semantic_lookup(query)
            if result:
                lookup_time = (time.time() - start_time) * 1000
                self._update_stats(hit=True, exact=False, lookup_time=lookup_time)
                
                result.lookup_time_ms = lookup_time
                return result
        
        # Cache miss
        lookup_time = (time.time() - start_time) * 1000
        self._update_stats(hit=False, lookup_time=lookup_time)
        
        return CacheLookupResult(
            hit=False,
            lookup_time_ms=lookup_time,
        )
    
    def put(
        self,
        query: str,
        response: str,
        ttl_seconds: Optional[int] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        lane: Optional[str] = None,
        quality_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CacheEntry:
        """
        Add an entry to the cache.
        """
        # Calculate TTL
        ttl = ttl_seconds or self.config.default_ttl_seconds
        ttl = max(self.config.min_ttl_seconds, min(ttl, self.config.max_ttl_seconds))
        
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        
        # Prepare response (with optional compression)
        original_size = len(response.encode())
        is_compressed = False
        compressed_size = original_size
        stored_response = response.encode()
        
        if self.config.enable_compression and original_size > 1024:
            compressed = zlib.compress(response.encode())
            if len(compressed) < original_size * 0.9:  # Only if 10%+ savings
                stored_response = compressed
                compressed_size = len(compressed)
                is_compressed = True
        
        # Create entry
        entry = CacheEntry(
            query=query,
            query_hash=self.matcher.get_hash(query),
            response=response,
            response_metadata=metadata or {},
            provider=provider,
            model=model,
            lane=lane,
            expires_at=expires_at,
            quality_score=quality_score,
            is_compressed=is_compressed,
            original_size=original_size,
            compressed_size=compressed_size,
        )
        
        # Check capacity and evict if needed
        self._ensure_capacity()
        
        # Store
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache_entries
                (id, query, query_hash, response, response_metadata,
                 provider, model, lane, created_at, accessed_at, expires_at,
                 hit_count, quality_score, is_compressed, original_size, compressed_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(entry.id),
                    entry.query,
                    entry.query_hash,
                    stored_response,
                    json.dumps(entry.response_metadata),
                    entry.provider,
                    entry.model,
                    entry.lane,
                    entry.created_at.isoformat(),
                    entry.accessed_at.isoformat(),
                    entry.expires_at.isoformat() if entry.expires_at else None,
                    entry.hit_count,
                    entry.quality_score,
                    1 if entry.is_compressed else 0,
                    entry.original_size,
                    entry.compressed_size,
                ),
            )
            conn.commit()
        
        logger.debug(
            "cache_entry_added",
            query_hash=entry.query_hash[:8],
            ttl=ttl,
            compressed=is_compressed,
        )
        
        return entry
    
    def invalidate(self, query: str) -> bool:
        """Invalidate a cache entry by query."""
        query_hash = self.matcher.get_hash(query)
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM cache_entries WHERE query_hash = ?",
                (query_hash,),
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def invalidate_by_id(self, entry_id: UUID) -> bool:
        """Invalidate a cache entry by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM cache_entries WHERE id = ?",
                (str(entry_id),),
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def clear(self) -> int:
        """Clear all cache entries."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM cache_entries")
            conn.commit()
            count = cursor.rowcount
        
        # Reset stats
        with self._stats_lock:
            self._stats = CacheStats()
        
        logger.info("cache_cleared", count=count)
        return count
    
    # ==================== Internal Operations ====================
    
    def _get_by_hash(self, query_hash: str) -> Optional[CacheEntry]:
        """Get entry by query hash."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM cache_entries WHERE query_hash = ?",
                (query_hash,),
            ).fetchone()
        
        return self._row_to_entry(row) if row else None
    
    def _semantic_lookup(self, query: str) -> Optional[CacheLookupResult]:
        """Perform semantic similarity lookup."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM cache_entries 
                WHERE (expires_at IS NULL OR expires_at > ?)
                ORDER BY accessed_at DESC
                LIMIT 1000
                """,
                (datetime.now(timezone.utc).isoformat(),),
            ).fetchall()
        
        if not rows:
            return None
        
        # Build candidates
        candidates = [(row["query"], row) for row in rows]
        
        # Find best match
        result = self.matcher.find_best_match(query, candidates)
        
        if result:
            row, score = result
            entry = self._row_to_entry(row)
            entry.touch()
            self._update_access(entry)
            
            return CacheLookupResult(
                hit=True,
                entry=entry,
                match_type="semantic",
                similarity_score=score,
            )
        
        return None
    
    def _row_to_entry(self, row: sqlite3.Row) -> CacheEntry:
        """Convert database row to CacheEntry."""
        response_data = row["response"]
        
        # Decompress if needed
        if row["is_compressed"]:
            response_data = zlib.decompress(response_data).decode()
        else:
            response_data = response_data.decode() if isinstance(response_data, bytes) else response_data
        
        return CacheEntry(
            id=UUID(row["id"]),
            query=row["query"],
            query_hash=row["query_hash"],
            response=response_data,
            response_metadata=json.loads(row["response_metadata"]) if row["response_metadata"] else {},
            provider=row["provider"],
            model=row["model"],
            lane=row["lane"],
            created_at=datetime.fromisoformat(row["created_at"]),
            accessed_at=datetime.fromisoformat(row["accessed_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
            hit_count=row["hit_count"],
            quality_score=row["quality_score"],
            is_compressed=bool(row["is_compressed"]),
            original_size=row["original_size"],
            compressed_size=row["compressed_size"],
        )
    
    def _update_access(self, entry: CacheEntry) -> None:
        """Update access timestamp and hit count."""
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE cache_entries 
                SET accessed_at = ?, hit_count = hit_count + 1
                WHERE id = ?
                """,
                (entry.accessed_at.isoformat(), str(entry.id)),
            )
            conn.commit()
    
    def _update_stats(
        self,
        hit: bool,
        exact: bool = False,
        lookup_time: float = 0.0,
    ) -> None:
        """Update cache statistics."""
        with self._stats_lock:
            if hit:
                self._stats.cache_hits += 1
                if exact:
                    self._stats.exact_hits += 1
                else:
                    self._stats.semantic_hits += 1
            else:
                self._stats.cache_misses += 1
            
            # Update average lookup time
            total = self._stats.total_requests
            if total > 0:
                prev_avg = self._stats.avg_lookup_time_ms
                self._stats.avg_lookup_time_ms = (
                    (prev_avg * (total - 1) + lookup_time) / total
                )
    
    def _ensure_capacity(self) -> None:
        """Ensure cache has capacity, evict if needed."""
        with self._get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) as cnt FROM cache_entries"
            ).fetchone()["cnt"]
        
        if count >= self.config.max_entries:
            self._evict(self.config.eviction_batch_size)
    
    def _evict(self, count: int) -> int:
        """Evict entries based on strategy."""
        strategy = self.config.eviction_strategy
        
        with self._get_connection() as conn:
            if strategy == EvictionStrategy.LRU:
                cursor = conn.execute(
                    """
                    DELETE FROM cache_entries WHERE id IN (
                        SELECT id FROM cache_entries 
                        ORDER BY accessed_at ASC LIMIT ?
                    )
                    """,
                    (count,),
                )
            elif strategy == EvictionStrategy.LFU:
                cursor = conn.execute(
                    """
                    DELETE FROM cache_entries WHERE id IN (
                        SELECT id FROM cache_entries 
                        ORDER BY hit_count ASC LIMIT ?
                    )
                    """,
                    (count,),
                )
            elif strategy == EvictionStrategy.FIFO:
                cursor = conn.execute(
                    """
                    DELETE FROM cache_entries WHERE id IN (
                        SELECT id FROM cache_entries 
                        ORDER BY created_at ASC LIMIT ?
                    )
                    """,
                    (count,),
                )
            else:  # TTL
                cursor = conn.execute(
                    """
                    DELETE FROM cache_entries 
                    WHERE expires_at < ?
                    """,
                    (datetime.now(timezone.utc).isoformat(),),
                )
            
            conn.commit()
            evicted = cursor.rowcount
        
        with self._stats_lock:
            self._stats.evicted_count += evicted
        
        logger.debug("cache_evicted", count=evicted, strategy=strategy.value)
        return evicted
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM cache_entries WHERE expires_at < ?",
                (datetime.now(timezone.utc).isoformat(),),
            )
            conn.commit()
            count = cursor.rowcount
        
        with self._stats_lock:
            self._stats.expired_count += count
        
        logger.info("cache_expired_cleaned", count=count)
        return count
    
    # ==================== Stats & Info ====================
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT 
                    COUNT(*) as count,
                    SUM(compressed_size) as total_size,
                    AVG(quality_score) as avg_quality
                FROM cache_entries
                """
            ).fetchone()
        
        stats = CacheStats()
        with self._stats_lock:
            stats.total_requests = self._stats.total_requests
            stats.cache_hits = self._stats.cache_hits
            stats.cache_misses = self._stats.cache_misses
            stats.exact_hits = self._stats.exact_hits
            stats.semantic_hits = self._stats.semantic_hits
            stats.avg_lookup_time_ms = self._stats.avg_lookup_time_ms
            stats.expired_count = self._stats.expired_count
            stats.evicted_count = self._stats.evicted_count
        
        stats.total_entries = row["count"] or 0
        stats.total_size_bytes = row["total_size"] or 0
        stats.avg_entry_size_bytes = (
            stats.total_size_bytes // stats.total_entries 
            if stats.total_entries > 0 else 0
        )
        stats.avg_quality_score = row["avg_quality"]
        
        return stats
    
    def get_entries(
        self,
        limit: int = 100,
        include_expired: bool = False,
    ) -> List[CacheEntry]:
        """Get cache entries."""
        with self._get_connection() as conn:
            if include_expired:
                rows = conn.execute(
                    "SELECT * FROM cache_entries ORDER BY accessed_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM cache_entries 
                    WHERE expires_at IS NULL OR expires_at > ?
                    ORDER BY accessed_at DESC LIMIT ?
                    """,
                    (datetime.now(timezone.utc).isoformat(), limit),
                ).fetchall()
        
        return [self._row_to_entry(row) for row in rows]


def get_cache_manager() -> SmartCacheManager:
    """Get the singleton cache manager."""
    return SmartCacheManager()
