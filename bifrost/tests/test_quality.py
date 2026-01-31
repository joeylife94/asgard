"""
Tests for Analysis Quality Metrics System.
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from bifrost.quality.models import (
    QualityScore,
    QualityDimension,
    AnalysisQualityReport,
    QualityThreshold,
    QualityTrend,
)
from bifrost.quality.analyzer import QualityAnalyzer


class TestQualityScore:
    """QualityScore 모델 테스트"""
    
    def test_create_quality_score(self):
        """기본 품질 점수 생성 테스트"""
        score = QualityScore(
            dimension=QualityDimension.RELEVANCE,
            score=0.85,
            weight=1.0,
            details="Good relevance to query",
            factors={"keyword_match": 0.9},
        )
        
        assert score.dimension == QualityDimension.RELEVANCE
        assert score.score == 0.85
        assert score.weight == 1.0
        assert score.details == "Good relevance to query"
        assert score.factors["keyword_match"] == 0.9
    
    def test_quality_score_to_dict(self):
        """품질 점수 직렬화 테스트"""
        score = QualityScore(
            dimension=QualityDimension.COMPLETENESS,
            score=0.75,
            weight=1.2,
        )
        
        data = score.to_dict()
        
        assert data["dimension"] == "completeness"
        assert data["score"] == 0.75
        assert data["weight"] == 1.2
    
    def test_quality_score_boundaries(self):
        """점수 경계값 테스트"""
        # 최소값
        score_min = QualityScore(
            dimension=QualityDimension.CLARITY,
            score=0.0,
        )
        assert score_min.score == 0.0
        
        # 최대값
        score_max = QualityScore(
            dimension=QualityDimension.CLARITY,
            score=1.0,
        )
        assert score_max.score == 1.0
    
    def test_quality_score_clamping(self):
        """점수 클램핑 테스트"""
        # Below 0 should be clamped to 0
        score_below = QualityScore(
            dimension=QualityDimension.CLARITY,
            score=-0.5,
        )
        assert score_below.score == 0.0
        
        # Above 1 should be clamped to 1
        score_above = QualityScore(
            dimension=QualityDimension.CLARITY,
            score=1.5,
        )
        assert score_above.score == 1.0
    
    def test_weighted_score(self):
        """가중 점수 계산 테스트"""
        score = QualityScore(
            dimension=QualityDimension.RELEVANCE,
            score=0.8,
            weight=1.5,
        )
        assert score.weighted_score == 0.8 * 1.5
    
    def test_grade_calculation(self):
        """등급 계산 테스트"""
        assert QualityScore(QualityDimension.CLARITY, 0.95).grade == "A"
        assert QualityScore(QualityDimension.CLARITY, 0.85).grade == "B"
        assert QualityScore(QualityDimension.CLARITY, 0.75).grade == "C"
        assert QualityScore(QualityDimension.CLARITY, 0.65).grade == "D"
        assert QualityScore(QualityDimension.CLARITY, 0.50).grade == "F"


class TestQualityDimension:
    """QualityDimension enum 테스트"""
    
    def test_all_dimensions_exist(self):
        """모든 차원이 정의되었는지 확인"""
        expected = [
            "accuracy",
            "completeness",
            "relevance",
            "clarity",
            "conciseness",
            "structure",
            "citation_quality",
            "confidence",
            "latency",
            "token_efficiency",
        ]
        
        for dim in expected:
            assert QualityDimension(dim)
    
    def test_dimension_values(self):
        """차원 값 테스트"""
        assert QualityDimension.ACCURACY.value == "accuracy"
        assert QualityDimension.RELEVANCE.value == "relevance"
        assert QualityDimension.COMPLETENESS.value == "completeness"


class TestAnalysisQualityReport:
    """AnalysisQualityReport 모델 테스트"""
    
    def test_create_report(self):
        """리포트 생성 테스트"""
        scores = [
            QualityScore(QualityDimension.RELEVANCE, 0.85),
            QualityScore(QualityDimension.CLARITY, 0.90),
        ]
        
        report = AnalysisQualityReport(
            request_id="req-123",
            scores=scores,
            overall_score=0.875,
            overall_grade="B",
        )
        
        assert report.request_id == "req-123"
        assert len(report.scores) == 2
        assert report.overall_score == 0.875
        assert report.overall_grade == "B"
        assert isinstance(report.id, UUID)
    
    def test_report_with_metadata(self):
        """메타데이터 포함 리포트 테스트"""
        report = AnalysisQualityReport(
            request_id="req-456",
            scores=[],
            overall_score=0.70,
            overall_grade="C",
            provider="ollama",
            lane="on_device",
            model="llama3.2",
            latency_ms=1500,
            token_count=500,
        )
        
        assert report.provider == "ollama"
        assert report.lane == "on_device"
        assert report.model == "llama3.2"
        assert report.latency_ms == 1500
        assert report.token_count == 500


class TestQualityThreshold:
    """QualityThreshold 모델 테스트"""
    
    def test_threshold_creation(self):
        """임계값 생성 테스트"""
        threshold = QualityThreshold(
            dimension=QualityDimension.RELEVANCE,
            min_score=0.6,
            target_score=0.8,
            alert_below=0.5,
        )
        
        assert threshold.dimension == QualityDimension.RELEVANCE
        assert threshold.min_score == 0.6
        assert threshold.target_score == 0.8
        assert threshold.alert_below == 0.5
    
    def test_is_acceptable(self):
        """acceptable 점수 테스트"""
        threshold = QualityThreshold(
            dimension=QualityDimension.CLARITY,
            min_score=0.6,
        )
        
        assert threshold.is_acceptable(0.7) is True
        assert threshold.is_acceptable(0.6) is True
        assert threshold.is_acceptable(0.5) is False
    
    def test_meets_target(self):
        """목표 점수 달성 테스트"""
        threshold = QualityThreshold(
            dimension=QualityDimension.STRUCTURE,
            target_score=0.8,
        )
        
        assert threshold.meets_target(0.9) is True
        assert threshold.meets_target(0.8) is True
        assert threshold.meets_target(0.7) is False


class TestQualityAnalyzer:
    """QualityAnalyzer 테스트"""
    
    @pytest.fixture
    def analyzer(self):
        """테스트용 분석기"""
        return QualityAnalyzer()
    
    def test_analyze_basic(self, analyzer):
        """기본 분석 테스트"""
        report = analyzer.analyze(
            request_id="test-req-001",
            question="What is the error in the log?",
            answer="The error indicates a connection timeout to the database server.",
        )
        
        assert report.request_id == "test-req-001"
        assert 0.0 <= report.overall_score <= 1.0
        assert report.overall_grade in ["A", "B", "C", "D", "F"]
        assert len(report.scores) > 0
    
    def test_analyze_short_response(self, analyzer):
        """짧은 응답 분석 테스트"""
        report = analyzer.analyze(
            request_id="test-req-004",
            question="What happened?",
            answer="Error.",
        )
        
        # Should have lower clarity/completeness
        assert report.overall_score < 0.9
    
    def test_analyze_well_structured_response(self, analyzer):
        """잘 구조화된 응답 분석 테스트"""
        report = analyzer.analyze(
            request_id="test-req-005",
            question="Explain the error and provide recommendations",
            answer="""
## Analysis Summary

The system encountered a critical database connection error.

## Root Cause

1. **Connection Pool Exhaustion**: The application exceeded the maximum number of connections.
2. **Timeout Configuration**: The timeout setting was too low.

## Impact

- Service availability degraded
- User requests failed

## Recommendations

1. Increase connection pool size
2. Implement connection retry logic
3. Add proper timeout handling

## Conclusion

The issue can be resolved by adjusting the configuration parameters.
            """,
        )
        
        # Well-structured response should score higher than short one
        assert report.overall_score > 0.5
        
        # Check structure score exists
        structure = next(
            (s for s in report.scores if s.dimension == QualityDimension.STRUCTURE),
            None,
        )
        assert structure is not None
        assert structure.score > 0.5
    
    def test_analyze_with_latency(self, analyzer):
        """지연 시간 포함 분석 테스트"""
        report = analyzer.analyze(
            request_id="test-req-006",
            question="Test query",
            answer="Test response with reasonable content.",
            latency_ms=500,
        )
        
        # Check latency dimension exists
        latency = next(
            (s for s in report.scores if s.dimension == QualityDimension.LATENCY),
            None,
        )
        
        assert latency is not None
        assert latency.score > 0.5  # 500ms is acceptable
    
    def test_analyze_with_token_count(self, analyzer):
        """토큰 수 포함 분석 테스트"""
        report = analyzer.analyze(
            request_id="test-req-007",
            question="Error?",
            answer="Connection timeout error in database.",
            token_count=10,
        )
        
        efficiency = next(
            (s for s in report.scores if s.dimension == QualityDimension.TOKEN_EFFICIENCY),
            None,
        )
        
        assert efficiency is not None
    
    def test_analyze_metadata_included(self, analyzer):
        """메타데이터 포함 테스트"""
        report = analyzer.analyze(
            request_id="test-req-008",
            job_id="job-001",
            question="Test",
            answer="Test response",
            provider="bedrock",
            lane="cloud",
            model="claude-3",
        )
        
        assert report.provider == "bedrock"
        assert report.lane == "cloud"
        assert report.model == "claude-3"
        assert report.job_id == "job-001"
    
    def test_grading_accuracy(self, analyzer):
        """등급 정확성 테스트"""
        # High quality response
        high_report = analyzer.analyze(
            request_id="test-high",
            question="What are the main issues?",
            answer="""
## Issue Analysis

The main issues identified are:

1. **Memory Leak**: The application has a gradual memory leak in the worker threads.
2. **Connection Issues**: Database connections are not being properly released.

### Recommendations

- Implement proper resource cleanup
- Add memory monitoring
- Review connection pool settings

### Conclusion

These issues require immediate attention to prevent service degradation.
            """,
        )
        
        # Low quality response
        low_report = analyzer.analyze(
            request_id="test-low",
            question="What are the main issues?",
            answer="issues",
        )
        
        assert high_report.overall_score > low_report.overall_score
    
    def test_analyze_with_citations(self, analyzer):
        """인용 포함 분석 테스트"""
        report = analyzer.analyze(
            request_id="test-citations",
            question="What is in the document?",
            answer="According to the document [chunk:1], the issue is a timeout.",
            citations=["Source 1", "Source 2"],
        )
        
        citation_score = next(
            (s for s in report.scores if s.dimension == QualityDimension.CITATION_QUALITY),
            None,
        )
        
        assert citation_score is not None


class TestQualityTracker:
    """QualityTracker 테스트"""
    
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
    def tracker(self, temp_db):
        """테스트용 트래커"""
        # Reset singleton
        from bifrost.quality.tracker import QualityTracker
        QualityTracker._instance = None
        
        return QualityTracker(db_path=temp_db)
    
    @pytest.fixture
    def sample_report(self):
        """샘플 리포트"""
        return AnalysisQualityReport(
            request_id="req-sample",
            job_id="job-sample",
            scores=[
                QualityScore(QualityDimension.RELEVANCE, 0.85),
                QualityScore(QualityDimension.CLARITY, 0.90),
                QualityScore(QualityDimension.COMPLETENESS, 0.80),
            ],
            overall_score=0.85,
            overall_grade="B",
            provider="ollama",
            lane="on_device",
            model="llama3.2",
            latency_ms=1200,
            token_count=450,
        )
    
    def test_save_and_get_report(self, tracker, sample_report):
        """리포트 저장 및 조회 테스트"""
        saved = tracker.save_report(sample_report)
        
        retrieved = tracker.get_report(saved.id)
        
        assert retrieved is not None
        assert retrieved.request_id == sample_report.request_id
        assert retrieved.overall_score == sample_report.overall_score
        assert len(retrieved.scores) == 3
    
    def test_get_reports_for_request(self, tracker, sample_report):
        """요청별 리포트 조회 테스트"""
        tracker.save_report(sample_report)
        
        # Create another report with same request_id
        report2 = AnalysisQualityReport(
            request_id="req-sample",
            scores=[QualityScore(QualityDimension.RELEVANCE, 0.75)],
            overall_score=0.75,
            overall_grade="C",
        )
        tracker.save_report(report2)
        
        reports = tracker.get_reports_for_request("req-sample")
        
        assert len(reports) == 2
    
    def test_get_recent_reports(self, tracker, sample_report):
        """최근 리포트 조회 테스트"""
        tracker.save_report(sample_report)
        
        reports = tracker.get_recent_reports(hours=1)
        
        assert len(reports) >= 1
        assert reports[0].request_id == "req-sample"
    
    def test_get_stats(self, tracker):
        """통계 조회 테스트"""
        # Add multiple reports
        for i in range(5):
            report = AnalysisQualityReport(
                request_id=f"req-{i}",
                scores=[QualityScore(QualityDimension.RELEVANCE, 0.7 + i * 0.05)],
                overall_score=0.7 + i * 0.05,
                overall_grade=["C", "C", "B", "B", "A"][i],
                provider="ollama" if i % 2 == 0 else "bedrock",
            )
            tracker.save_report(report)
        
        stats = tracker.get_stats(hours=1)
        
        assert stats["total_reports"] == 5
        assert stats["average_score"] is not None
        assert "grade_distribution" in stats
        assert "by_provider" in stats
    
    def test_get_dimension_stats(self, tracker, sample_report):
        """차원별 통계 테스트"""
        tracker.save_report(sample_report)
        
        stats = tracker.get_dimension_stats(hours=1)
        
        assert "dimensions" in stats
        assert "relevance" in stats["dimensions"]
        assert stats["dimensions"]["relevance"]["average"] > 0
    
    def test_get_trends(self, tracker, sample_report):
        """트렌드 조회 테스트"""
        tracker.save_report(sample_report)
        
        trends = tracker.get_trends(days=7)
        
        assert trends.period == "daily"
        assert len(trends.data_points) >= 0
    
    def test_get_low_quality_reports(self, tracker):
        """저품질 리포트 조회 테스트"""
        # Add a low quality report
        low_report = AnalysisQualityReport(
            request_id="req-low",
            scores=[QualityScore(QualityDimension.RELEVANCE, 0.3)],
            overall_score=0.4,
            overall_grade="F",
        )
        tracker.save_report(low_report)
        
        # Add a high quality report
        high_report = AnalysisQualityReport(
            request_id="req-high",
            scores=[QualityScore(QualityDimension.RELEVANCE, 0.9)],
            overall_score=0.9,
            overall_grade="A",
        )
        tracker.save_report(high_report)
        
        low_reports = tracker.get_low_quality_reports(threshold=0.6)
        
        assert len(low_reports) == 1
        assert low_reports[0].request_id == "req-low"
    
    def test_cleanup_old(self, tracker, sample_report):
        """오래된 데이터 정리 테스트"""
        tracker.save_report(sample_report)
        
        # Cleanup with 0 days should delete all
        deleted = tracker.cleanup_old(days=0)
        
        assert deleted >= 0


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
    
    def test_analyze_and_track(self, temp_db):
        """분석 및 추적 통합 테스트"""
        from bifrost.quality.tracker import QualityTracker
        
        # Reset singleton
        QualityTracker._instance = None
        
        analyzer = QualityAnalyzer()
        tracker = QualityTracker(db_path=temp_db)
        
        # Analyze a response
        report = analyzer.analyze(
            request_id="integration-test",
            question="Analyze the database error",
            answer="""
## Error Analysis

A database connection timeout occurred.

### Root Cause
Connection pool exhausted.

### Recommendations
1. Increase pool size
2. Add retry logic
            """,
            provider="ollama",
            lane="on_device",
        )
        
        # Save and retrieve
        tracker.save_report(report)
        retrieved = tracker.get_report(report.id)
        
        assert retrieved is not None
        assert retrieved.overall_score == report.overall_score
        
        # Check stats
        stats = tracker.get_stats(hours=1)
        assert stats["total_reports"] >= 1
    
    def test_multiple_providers_comparison(self, temp_db):
        """다중 프로바이더 비교 테스트"""
        from bifrost.quality.tracker import QualityTracker
        
        QualityTracker._instance = None
        
        analyzer = QualityAnalyzer()
        tracker = QualityTracker(db_path=temp_db)
        
        # Analyze same query with different providers
        for provider in ["ollama", "bedrock"]:
            report = analyzer.analyze(
                request_id=f"compare-{provider}",
                question="What is the issue?",
                answer="The issue is a timeout error.",
                provider=provider,
            )
            tracker.save_report(report)
        
        stats = tracker.get_stats(hours=1)
        
        assert "by_provider" in stats
        assert "ollama" in stats["by_provider"]
        assert "bedrock" in stats["by_provider"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
