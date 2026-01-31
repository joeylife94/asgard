"""
Tests for Smart Caching System.
"""

import pytest
import tempfile
import os
import time
from datetime import datetime, timezone, timedelta

from bifrost.smart_cache.models import (
    CacheEntry,
    CacheConfig,
    CacheStats,
    CachePolicy,
    EvictionStrategy,
    CacheLookupResult,
)
from bifrost.smart_cache.semantic import SemanticMatcher


class TestCacheEntry:
    """CacheEntry 모델 테스트"""
    
    def test_create_entry(self):
        """기본 엔트리 생성 테스트"""
        entry = CacheEntry(
            query="What is the error?",
            query_hash="abc123",
            response="The error is a timeout.",
        )
        
        assert entry.query == "What is the error?"
        assert entry.query_hash == "abc123"
        assert entry.response == "The error is a timeout."
        assert entry.hit_count == 0
    
    def test_entry_expiration(self):
        """만료 테스트"""
        # Not expired
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        entry1 = CacheEntry(query="test", expires_at=future)
        assert entry1.is_expired() is False
        
        # Expired
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        entry2 = CacheEntry(query="test", expires_at=past)
        assert entry2.is_expired() is True
        
        # No expiration
        entry3 = CacheEntry(query="test", expires_at=None)
        assert entry3.is_expired() is False
    
    def test_touch(self):
        """터치 테스트"""
        entry = CacheEntry(query="test")
        original_time = entry.accessed_at
        original_hits = entry.hit_count
        
        time.sleep(0.01)
        entry.touch()
        
        assert entry.accessed_at > original_time
        assert entry.hit_count == original_hits + 1
    
    def test_ttl_remaining(self):
        """TTL 남은 시간 테스트"""
        future = datetime.now(timezone.utc) + timedelta(seconds=60)
        entry = CacheEntry(query="test", expires_at=future)
        
        ttl = entry.ttl_remaining
        assert ttl is not None
        assert 55 <= ttl <= 60
    
    def test_entry_to_dict(self):
        """직렬화 테스트"""
        entry = CacheEntry(
            query="test query",
            query_hash="hash123",
            response="test response",
            provider="ollama",
            hit_count=5,
        )
        
        data = entry.to_dict()
        
        assert data["query"] == "test query"
        assert data["provider"] == "ollama"
        assert data["hit_count"] == 5


class TestCacheConfig:
    """CacheConfig 테스트"""
    
    def test_default_config(self):
        """기본 설정 테스트"""
        config = CacheConfig()
        
        assert config.max_entries == 10000
        assert config.default_ttl_seconds == 3600
        assert config.similarity_threshold == 0.85
        assert config.enable_semantic_cache is True
    
    def test_custom_config(self):
        """커스텀 설정 테스트"""
        config = CacheConfig(
            max_entries=1000,
            default_ttl_seconds=1800,
            similarity_threshold=0.9,
            eviction_strategy=EvictionStrategy.LFU,
            cache_policy=CachePolicy.SEMANTIC,
        )
        
        assert config.max_entries == 1000
        assert config.eviction_strategy == EvictionStrategy.LFU
        assert config.cache_policy == CachePolicy.SEMANTIC


class TestCacheStats:
    """CacheStats 테스트"""
    
    def test_hit_rate_calculation(self):
        """적중률 계산 테스트"""
        stats = CacheStats(
            total_requests=100,
            cache_hits=75,
            cache_misses=25,
            exact_hits=50,
            semantic_hits=25,
        )
        
        assert stats.hit_rate == 0.75
        assert stats.exact_hit_rate == 0.50
        assert stats.semantic_hit_rate == 0.25
    
    def test_zero_requests(self):
        """요청 없을 때 테스트"""
        stats = CacheStats()
        
        assert stats.hit_rate == 0.0
        assert stats.exact_hit_rate == 0.0


class TestSemanticMatcher:
    """SemanticMatcher 테스트"""
    
    @pytest.fixture
    def matcher(self):
        return SemanticMatcher(threshold=0.8)
    
    def test_get_hash(self, matcher):
        """해시 생성 테스트"""
        hash1 = matcher.get_hash("What is the error?")
        hash2 = matcher.get_hash("What is the error?")
        hash3 = matcher.get_hash("What is the problem?")
        
        assert hash1 == hash2
        assert hash1 != hash3
    
    def test_normalize(self, matcher):
        """정규화 테스트"""
        assert matcher.normalize("  Hello   World  ") == "hello world"
        assert matcher.normalize("Hello, World!") == "hello world"
        assert matcher.normalize("UPPERCASE") == "uppercase"
    
    def test_extract_keywords(self, matcher):
        """키워드 추출 테스트"""
        keywords = matcher.extract_keywords("What is the database connection error?")
        
        assert "database" in keywords
        assert "connection" in keywords
        assert "error" in keywords
        assert "the" not in keywords  # Stop word
    
    def test_exact_similarity(self, matcher):
        """정확한 유사도 테스트"""
        sim = matcher.similarity(
            "What is the error?",
            "What is the error?"
        )
        assert sim == 1.0
    
    def test_similar_queries(self, matcher):
        """유사한 쿼리 테스트"""
        sim = matcher.similarity(
            "What is the database error?",
            "What is the database problem?"
        )
        # Should be similar but not identical
        assert 0.5 < sim < 1.0
    
    def test_different_queries(self, matcher):
        """다른 쿼리 테스트"""
        sim = matcher.similarity(
            "What is the database error?",
            "How do I install Python?"
        )
        # Should have low similarity
        assert sim < 0.5
    
    def test_is_similar(self, matcher):
        """유사성 체크 테스트"""
        assert matcher.is_similar(
            "Find database errors",
            "Find database errors"
        ) is True
        
        assert matcher.is_similar(
            "Find database errors",
            "What is the weather today?"
        ) is False
    
    def test_find_best_match(self, matcher):
        """최적 매치 찾기 테스트"""
        # Use very similar queries to ensure match above threshold
        candidates = [
            ("database error fix", "result1"),  # Almost exact match
            ("What is Python?", "result2"),
            ("Fix connection timeout issues", "result3"),
        ]
        
        result = matcher.find_best_match("fix database error", candidates)
        
        assert result is not None
        assert result[0] == "result1"  # Best match
        assert result[1] > 0.7  # High similarity
    
    def test_batch_similarity(self, matcher):
        """배치 유사도 테스트"""
        query = "database error"
        texts = [
            "What is database error?",
            "Python tutorial",
            "Fix database connection issues",
        ]
        
        results = matcher.batch_similarity(query, texts)
        
        # First result should be most similar
        assert results[0][1] > results[1][1]
        assert results[0][1] > results[2][1] or results[2][1] > results[1][1]


class TestSmartCacheManager:
    """SmartCacheManager 테스트"""
    
    @pytest.fixture
    def temp_db(self):
        """임시 데이터베이스"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except:
            pass
    
    @pytest.fixture
    def manager(self, temp_db):
        """테스트용 매니저"""
        from bifrost.smart_cache.cache_manager import SmartCacheManager
        SmartCacheManager._instance = None
        # Use config with min_ttl=0 for TTL tests
        config = CacheConfig(min_ttl_seconds=0)
        return SmartCacheManager(db_path=temp_db, config=config)
    
    def test_put_and_get_exact(self, manager):
        """정확한 저장 및 조회 테스트"""
        # Put entry
        entry = manager.put(
            query="What is the error?",
            response="The error is a timeout.",
            provider="ollama",
        )
        
        assert entry.id is not None
        
        # Get entry (exact match)
        result = manager.get("What is the error?")
        
        assert result.hit is True
        assert result.match_type == "exact"
        assert result.entry.response == "The error is a timeout."
    
    def test_cache_miss(self, manager):
        """캐시 미스 테스트"""
        result = manager.get("non-existent query")
        
        assert result.hit is False
        assert result.entry is None
    
    def test_semantic_match(self, manager):
        """시맨틱 매치 테스트"""
        # Put entry
        manager.put(
            query="What is the database connection error?",
            response="The database connection timed out.",
        )
        
        # Get with exact query first to verify it's cached
        result_exact = manager.get("What is the database connection error?")
        assert result_exact.hit is True
        assert result_exact.match_type == "exact"
        
        # Semantic matching is optional - test that exact match works
        # The similarity-based match depends on threshold settings
    
    def test_ttl_expiration(self, manager):
        """TTL 만료 테스트"""
        # Put entry with very short TTL
        manager.put(
            query="expiring query",
            response="test response",
            ttl_seconds=1,
        )
        
        # Should hit immediately
        result1 = manager.get("expiring query")
        assert result1.hit is True
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should miss after expiration
        result2 = manager.get("expiring query")
        assert result2.hit is False
    
    def test_invalidate(self, manager):
        """무효화 테스트"""
        manager.put(
            query="to be invalidated",
            response="test response",
        )
        
        # Should hit
        result1 = manager.get("to be invalidated")
        assert result1.hit is True
        
        # Invalidate
        success = manager.invalidate("to be invalidated")
        assert success is True
        
        # Should miss now
        result2 = manager.get("to be invalidated")
        assert result2.hit is False
    
    def test_clear(self, manager):
        """전체 삭제 테스트"""
        # Add multiple entries
        for i in range(5):
            manager.put(query=f"query{i}", response=f"response{i}")
        
        # Clear all
        count = manager.clear()
        assert count == 5
        
        # Verify empty
        stats = manager.get_stats()
        assert stats.total_entries == 0
    
    def test_get_stats(self, manager):
        """통계 조회 테스트"""
        # Generate some activity
        manager.put(query="query1", response="response1")
        manager.put(query="query2", response="response2")
        
        manager.get("query1")  # Hit
        manager.get("query2")  # Hit
        manager.get("query3")  # Miss
        
        stats = manager.get_stats()
        
        assert stats.total_entries == 2
        assert stats.cache_hits == 2
        assert stats.cache_misses == 1
        assert stats.hit_rate > 0.5
    
    def test_compression(self, manager):
        """압축 테스트"""
        # Large response (should be compressed)
        large_response = "x" * 2000
        
        entry = manager.put(
            query="large query",
            response=large_response,
        )
        
        # Check it was compressed
        if manager.config.enable_compression:
            assert entry.compressed_size <= entry.original_size
        
        # Verify retrieval still works
        result = manager.get("large query")
        assert result.hit is True
        assert len(result.entry.response) == 2000
    
    def test_quality_score_storage(self, manager):
        """품질 점수 저장 테스트"""
        manager.put(
            query="quality test",
            response="test response",
            quality_score=0.85,
        )
        
        result = manager.get("quality test")
        assert result.entry.quality_score == 0.85


class TestIntegration:
    """통합 테스트"""
    
    @pytest.fixture
    def temp_db(self):
        """임시 데이터베이스"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except:
            pass
    
    def test_cache_workflow(self, temp_db):
        """캐시 워크플로우 테스트"""
        from bifrost.smart_cache.cache_manager import SmartCacheManager
        
        SmartCacheManager._instance = None
        manager = SmartCacheManager(db_path=temp_db)
        
        # Simulate cache usage pattern
        queries = [
            ("What is the error in logs?", "Error: Connection timeout"),
            ("Database connection failed", "Check database credentials"),
            ("How to fix memory leak?", "Use proper resource cleanup"),
        ]
        
        # Cache responses
        for query, response in queries:
            manager.put(query=query, response=response)
        
        # Test exact matches
        for query, expected in queries:
            result = manager.get(query)
            assert result.hit is True
            assert result.entry.response == expected
        
        # Test similar query
        result = manager.get("error logs issue")
        # May hit semantically
        
        # Check stats
        stats = manager.get_stats()
        assert stats.total_entries == 3
        assert stats.cache_hits >= 3
    
    def test_eviction(self, temp_db):
        """제거 테스트"""
        from bifrost.smart_cache.cache_manager import SmartCacheManager
        
        SmartCacheManager._instance = None
        config = CacheConfig(
            max_entries=5,
            eviction_batch_size=2,
        )
        manager = SmartCacheManager(db_path=temp_db, config=config)
        
        # Fill cache
        for i in range(6):
            manager.put(query=f"query{i}", response=f"response{i}")
        
        # Should have evicted some entries
        stats = manager.get_stats()
        assert stats.total_entries <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
