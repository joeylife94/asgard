"""
Data models for A/B Testing Framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4


class ExperimentStatus(str, Enum):
    """Experiment lifecycle status."""
    DRAFT = "draft"  # Not started yet
    RUNNING = "running"  # Currently active
    PAUSED = "paused"  # Temporarily stopped
    COMPLETED = "completed"  # Finished successfully
    STOPPED = "stopped"  # Manually stopped early


class VariantType(str, Enum):
    """Type of variant configuration."""
    CONTROL = "control"  # Baseline (existing behavior)
    TREATMENT = "treatment"  # New behavior to test


@dataclass
class Variant:
    """
    A variant in an experiment (control or treatment).
    """
    name: str
    variant_type: VariantType
    weight: float = 50.0  # Traffic percentage (0-100)
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Provider/model configuration
    provider: Optional[str] = None
    model: Optional[str] = None
    lane: Optional[str] = None
    
    # Additional parameters
    prompt_template: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "variant_type": self.variant_type.value,
            "weight": self.weight,
            "config": self.config,
            "provider": self.provider,
            "model": self.model,
            "lane": self.lane,
            "prompt_template": self.prompt_template,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Variant":
        return cls(
            name=data["name"],
            variant_type=VariantType(data["variant_type"]),
            weight=data.get("weight", 50.0),
            config=data.get("config", {}),
            provider=data.get("provider"),
            model=data.get("model"),
            lane=data.get("lane"),
            prompt_template=data.get("prompt_template"),
            temperature=data.get("temperature"),
            max_tokens=data.get("max_tokens"),
        )


@dataclass
class TrafficAllocation:
    """
    Traffic allocation rules for an experiment.
    """
    # User segment targeting (optional)
    target_users: Optional[List[str]] = None  # Specific user IDs
    target_percentage: float = 100.0  # % of eligible traffic
    
    # Request filtering
    include_patterns: Optional[List[str]] = None  # Query patterns to include
    exclude_patterns: Optional[List[str]] = None  # Query patterns to exclude
    
    # Time-based allocation
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def is_eligible(
        self,
        user_id: Optional[str] = None,
        query: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Check if a request is eligible for this experiment."""
        # Check user targeting
        if self.target_users is not None and user_id not in self.target_users:
            return False
        
        # Check time window
        now = timestamp or datetime.now(timezone.utc)
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        
        # Check query patterns
        if query:
            if self.include_patterns:
                if not any(p.lower() in query.lower() for p in self.include_patterns):
                    return False
            if self.exclude_patterns:
                if any(p.lower() in query.lower() for p in self.exclude_patterns):
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_users": self.target_users,
            "target_percentage": self.target_percentage,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class VariantMetrics:
    """
    Aggregated metrics for a variant.
    """
    variant_name: str
    sample_count: int = 0
    
    # Quality metrics
    avg_quality_score: float = 0.0
    quality_scores: List[float] = field(default_factory=list)
    
    # Performance metrics
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # User satisfaction (if feedback available)
    avg_satisfaction: Optional[float] = None
    positive_feedback_count: int = 0
    negative_feedback_count: int = 0
    
    # Cost metrics
    total_tokens: int = 0
    estimated_cost: float = 0.0
    
    # Error metrics
    error_count: int = 0
    error_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "variant_name": self.variant_name,
            "sample_count": self.sample_count,
            "avg_quality_score": round(self.avg_quality_score, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "p50_latency_ms": round(self.p50_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "p99_latency_ms": round(self.p99_latency_ms, 2),
            "avg_satisfaction": round(self.avg_satisfaction, 4) if self.avg_satisfaction else None,
            "positive_feedback_count": self.positive_feedback_count,
            "negative_feedback_count": self.negative_feedback_count,
            "total_tokens": self.total_tokens,
            "estimated_cost": round(self.estimated_cost, 4),
            "error_count": self.error_count,
            "error_rate": round(self.error_rate, 4),
        }


@dataclass
class StatisticalResult:
    """
    Statistical analysis result comparing variants.
    """
    is_significant: bool
    confidence_level: float  # 0.90, 0.95, 0.99
    p_value: float
    effect_size: float  # Cohen's d or similar
    
    winner: Optional[str] = None  # Variant name
    improvement_percent: float = 0.0
    
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_significant": self.is_significant,
            "confidence_level": self.confidence_level,
            "p_value": round(self.p_value, 6),
            "effect_size": round(self.effect_size, 4),
            "winner": self.winner,
            "improvement_percent": round(self.improvement_percent, 2),
            "recommendation": self.recommendation,
        }


@dataclass
class ExperimentResult:
    """
    Complete result of an experiment.
    """
    experiment_id: UUID
    experiment_name: str
    
    status: ExperimentStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_hours: float = 0.0
    
    total_samples: int = 0
    variants_metrics: List[VariantMetrics] = field(default_factory=list)
    
    # Statistical analysis
    quality_comparison: Optional[StatisticalResult] = None
    latency_comparison: Optional[StatisticalResult] = None
    satisfaction_comparison: Optional[StatisticalResult] = None
    
    # Overall recommendation
    recommended_variant: Optional[str] = None
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": str(self.experiment_id),
            "experiment_name": self.experiment_name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_hours": round(self.duration_hours, 2),
            "total_samples": self.total_samples,
            "variants_metrics": [v.to_dict() for v in self.variants_metrics],
            "quality_comparison": self.quality_comparison.to_dict() if self.quality_comparison else None,
            "latency_comparison": self.latency_comparison.to_dict() if self.latency_comparison else None,
            "satisfaction_comparison": self.satisfaction_comparison.to_dict() if self.satisfaction_comparison else None,
            "recommended_variant": self.recommended_variant,
            "summary": self.summary,
        }


@dataclass
class ExperimentConfig:
    """
    Configuration for running an experiment.
    """
    # Primary metric for decision
    primary_metric: str = "quality_score"  # quality_score, latency, satisfaction
    
    # Minimum sample size
    min_samples_per_variant: int = 100
    
    # Statistical settings
    confidence_level: float = 0.95
    minimum_detectable_effect: float = 0.05  # 5% improvement
    
    # Auto-stopping rules
    auto_stop_on_significance: bool = False
    max_duration_hours: Optional[float] = None
    
    # Fallback settings
    fallback_to_control_on_error: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_metric": self.primary_metric,
            "min_samples_per_variant": self.min_samples_per_variant,
            "confidence_level": self.confidence_level,
            "minimum_detectable_effect": self.minimum_detectable_effect,
            "auto_stop_on_significance": self.auto_stop_on_significance,
            "max_duration_hours": self.max_duration_hours,
            "fallback_to_control_on_error": self.fallback_to_control_on_error,
        }


@dataclass
class Experiment:
    """
    A/B test experiment definition.
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    
    # Variants (control + treatments)
    variants: List[Variant] = field(default_factory=list)
    
    # Traffic allocation rules
    allocation: TrafficAllocation = field(default_factory=TrafficAllocation)
    
    # Experiment configuration
    config: ExperimentConfig = field(default_factory=ExperimentConfig)
    
    # State
    status: ExperimentStatus = ExperimentStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Metadata
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def get_control(self) -> Optional[Variant]:
        """Get the control variant."""
        for v in self.variants:
            if v.variant_type == VariantType.CONTROL:
                return v
        return None
    
    def get_treatments(self) -> List[Variant]:
        """Get all treatment variants."""
        return [v for v in self.variants if v.variant_type == VariantType.TREATMENT]
    
    def is_active(self) -> bool:
        """Check if experiment is currently running."""
        return self.status == ExperimentStatus.RUNNING
    
    def validate(self) -> List[str]:
        """Validate experiment configuration."""
        errors = []
        
        if not self.name:
            errors.append("Experiment name is required")
        
        if len(self.variants) < 2:
            errors.append("At least 2 variants required (control + treatment)")
        
        controls = [v for v in self.variants if v.variant_type == VariantType.CONTROL]
        if len(controls) != 1:
            errors.append("Exactly one control variant required")
        
        total_weight = sum(v.weight for v in self.variants)
        if abs(total_weight - 100.0) > 0.01:
            errors.append(f"Variant weights must sum to 100, got {total_weight}")
        
        for v in self.variants:
            if v.weight <= 0:
                errors.append(f"Variant '{v.name}' must have positive weight")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "variants": [v.to_dict() for v in self.variants],
            "allocation": self.allocation.to_dict(),
            "config": self.config.to_dict(),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_by": self.created_by,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Experiment":
        return cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            name=data.get("name", ""),
            description=data.get("description", ""),
            variants=[Variant.from_dict(v) for v in data.get("variants", [])],
            status=ExperimentStatus(data.get("status", "draft")),
            created_by=data.get("created_by"),
            tags=data.get("tags", []),
        )


@dataclass
class ExperimentAssignment:
    """
    Records a user/request assignment to a variant.
    """
    id: UUID = field(default_factory=uuid4)
    experiment_id: UUID = field(default_factory=uuid4)
    variant_name: str = ""
    
    # Request context
    request_id: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Assignment metadata
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Result tracking
    quality_score: Optional[float] = None
    latency_ms: Optional[int] = None
    satisfaction_score: Optional[float] = None
    error_occurred: bool = False
    token_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "experiment_id": str(self.experiment_id),
            "variant_name": self.variant_name,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "assigned_at": self.assigned_at.isoformat(),
            "quality_score": self.quality_score,
            "latency_ms": self.latency_ms,
            "satisfaction_score": self.satisfaction_score,
            "error_occurred": self.error_occurred,
            "token_count": self.token_count,
        }
