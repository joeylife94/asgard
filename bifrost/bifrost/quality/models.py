"""
Data models for Quality Metrics System.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4


class QualityDimension(str, Enum):
    """Dimensions of quality measurement."""
    
    # Content Quality
    ACCURACY = "accuracy"  # Correctness of information
    COMPLETENESS = "completeness"  # Coverage of relevant points
    RELEVANCE = "relevance"  # Alignment with the question
    
    # Response Quality
    CLARITY = "clarity"  # Readability and understandability
    CONCISENESS = "conciseness"  # Appropriate length/detail
    STRUCTURE = "structure"  # Organization and formatting
    
    # Technical Quality
    CITATION_QUALITY = "citation_quality"  # Source attribution quality
    CONFIDENCE = "confidence"  # Model confidence level
    
    # Performance
    LATENCY = "latency"  # Response time quality
    TOKEN_EFFICIENCY = "token_efficiency"  # Token usage efficiency


@dataclass
class QualityScore:
    """
    Individual quality score for a dimension.
    
    Score range: 0.0 (worst) to 1.0 (best)
    """
    
    dimension: QualityDimension
    score: float  # 0.0 - 1.0
    weight: float = 1.0  # Weight for weighted average
    details: Optional[str] = None
    factors: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Clamp score to valid range
        self.score = max(0.0, min(1.0, self.score))
    
    @property
    def weighted_score(self) -> float:
        return self.score * self.weight
    
    @property
    def grade(self) -> str:
        """Convert score to letter grade."""
        if self.score >= 0.9:
            return "A"
        elif self.score >= 0.8:
            return "B"
        elif self.score >= 0.7:
            return "C"
        elif self.score >= 0.6:
            return "D"
        else:
            return "F"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "score": round(self.score, 3),
            "weight": self.weight,
            "weighted_score": round(self.weighted_score, 3),
            "grade": self.grade,
            "details": self.details,
            "factors": self.factors,
        }


@dataclass
class QualityThreshold:
    """
    Quality thresholds for alerts and actions.
    """
    
    dimension: QualityDimension
    min_score: float = 0.6  # Minimum acceptable score
    target_score: float = 0.8  # Target score
    alert_below: float = 0.5  # Alert threshold
    
    def is_acceptable(self, score: float) -> bool:
        return score >= self.min_score
    
    def meets_target(self, score: float) -> bool:
        return score >= self.target_score
    
    def should_alert(self, score: float) -> bool:
        return score < self.alert_below


@dataclass
class AnalysisQualityReport:
    """
    Comprehensive quality report for an analysis.
    """
    
    id: UUID = field(default_factory=uuid4)
    request_id: str = ""
    job_id: Optional[str] = None
    
    # Individual scores
    scores: List[QualityScore] = field(default_factory=list)
    
    # Overall metrics
    overall_score: float = 0.0
    overall_grade: str = "N/A"
    
    # Context
    provider: Optional[str] = None
    lane: Optional[str] = None
    model: Optional[str] = None
    
    # Performance
    latency_ms: Optional[int] = None
    token_count: Optional[int] = None
    
    # Metadata
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    analysis_version: str = "1.0"
    
    def calculate_overall(self) -> None:
        """Calculate overall score from individual dimensions."""
        if not self.scores:
            self.overall_score = 0.0
            self.overall_grade = "N/A"
            return
        
        total_weight = sum(s.weight for s in self.scores)
        if total_weight == 0:
            self.overall_score = 0.0
        else:
            self.overall_score = sum(s.weighted_score for s in self.scores) / total_weight
        
        # Calculate grade
        if self.overall_score >= 0.9:
            self.overall_grade = "A"
        elif self.overall_score >= 0.8:
            self.overall_grade = "B"
        elif self.overall_score >= 0.7:
            self.overall_grade = "C"
        elif self.overall_score >= 0.6:
            self.overall_grade = "D"
        else:
            self.overall_grade = "F"
    
    def get_score(self, dimension: QualityDimension) -> Optional[QualityScore]:
        """Get score for a specific dimension."""
        for score in self.scores:
            if score.dimension == dimension:
                return score
        return None
    
    def get_weak_dimensions(self, threshold: float = 0.6) -> List[QualityScore]:
        """Get dimensions scoring below threshold."""
        return [s for s in self.scores if s.score < threshold]
    
    def get_strong_dimensions(self, threshold: float = 0.8) -> List[QualityScore]:
        """Get dimensions scoring above threshold."""
        return [s for s in self.scores if s.score >= threshold]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "request_id": self.request_id,
            "job_id": self.job_id,
            "scores": [s.to_dict() for s in self.scores],
            "overall_score": round(self.overall_score, 3),
            "overall_grade": self.overall_grade,
            "provider": self.provider,
            "lane": self.lane,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "token_count": self.token_count,
            "weak_dimensions": [s.dimension.value for s in self.get_weak_dimensions()],
            "strong_dimensions": [s.dimension.value for s in self.get_strong_dimensions()],
            "analyzed_at": self.analyzed_at.isoformat(),
        }


@dataclass
class QualityTrend:
    """Quality trends over time."""
    
    period: str  # "hourly", "daily", "weekly"
    dimension: Optional[QualityDimension] = None  # None for overall
    data_points: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period,
            "dimension": self.dimension.value if self.dimension else "overall",
            "data_points": self.data_points,
        }


@dataclass
class QualityBenchmark:
    """Benchmark scores for comparison."""
    
    name: str
    description: str
    scores: Dict[str, float] = field(default_factory=dict)  # dimension -> score
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def compare(self, report: AnalysisQualityReport) -> Dict[str, float]:
        """Compare a report against this benchmark."""
        comparison = {}
        for score in report.scores:
            benchmark_score = self.scores.get(score.dimension.value, 0.5)
            comparison[score.dimension.value] = score.score - benchmark_score
        return comparison
