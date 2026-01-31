"""
Feedback data models and schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4


class FeedbackType(str, Enum):
    """Types of feedback that can be collected."""
    
    # Quick reactions
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    
    # Detailed ratings
    RATING = "rating"  # 1-5 stars
    
    # Specific issues
    INACCURATE = "inaccurate"
    INCOMPLETE = "incomplete"
    IRRELEVANT = "irrelevant"
    TOO_SLOW = "too_slow"
    
    # Positive feedback
    HELPFUL = "helpful"
    ACCURATE = "accurate"
    WELL_FORMATTED = "well_formatted"


class FeedbackRating(int, Enum):
    """Star ratings for detailed feedback."""
    
    VERY_POOR = 1
    POOR = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


@dataclass
class Feedback:
    """
    User feedback for an AI analysis response.
    
    Attributes:
        id: Unique feedback identifier
        request_id: Associated analysis request ID
        job_id: Associated Heimdall job ID (if any)
        feedback_type: Type of feedback
        rating: Optional star rating (1-5)
        comment: Optional user comment
        tags: Optional categorization tags
        user_id: Anonymous user identifier (optional)
        session_id: Browser session ID for grouping
        metadata: Additional context (lane, provider, latency, etc.)
        created_at: Feedback submission timestamp
    """
    
    id: UUID = field(default_factory=uuid4)
    request_id: str = ""
    job_id: Optional[str] = None
    feedback_type: FeedbackType = FeedbackType.THUMBS_UP
    rating: Optional[int] = None
    comment: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_positive(self) -> bool:
        """Check if feedback is positive."""
        positive_types = {
            FeedbackType.THUMBS_UP,
            FeedbackType.HELPFUL,
            FeedbackType.ACCURATE,
            FeedbackType.WELL_FORMATTED,
        }
        if self.feedback_type in positive_types:
            return True
        if self.rating and self.rating >= 4:
            return True
        return False
    
    def is_negative(self) -> bool:
        """Check if feedback is negative."""
        negative_types = {
            FeedbackType.THUMBS_DOWN,
            FeedbackType.INACCURATE,
            FeedbackType.INCOMPLETE,
            FeedbackType.IRRELEVANT,
            FeedbackType.TOO_SLOW,
        }
        if self.feedback_type in negative_types:
            return True
        if self.rating and self.rating <= 2:
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        return {
            "id": str(self.id),
            "request_id": self.request_id,
            "job_id": self.job_id,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "comment": self.comment,
            "tags": self.tags,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "is_positive": self.is_positive(),
            "is_negative": self.is_negative(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Feedback":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]) if isinstance(data.get("id"), str) else data.get("id", uuid4()),
            request_id=data.get("request_id", ""),
            job_id=data.get("job_id"),
            feedback_type=FeedbackType(data.get("feedback_type", "thumbs_up")),
            rating=data.get("rating"),
            comment=data.get("comment"),
            tags=data.get("tags", []),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(timezone.utc),
        )


@dataclass
class FeedbackStats:
    """
    Aggregated feedback statistics.
    
    Attributes:
        total_count: Total number of feedback entries
        positive_count: Number of positive feedback entries
        negative_count: Number of negative feedback entries
        neutral_count: Number of neutral feedback entries
        average_rating: Average star rating (if applicable)
        satisfaction_rate: Percentage of positive feedback
        type_distribution: Count by feedback type
        tag_distribution: Count by tags
        time_period_start: Start of the analysis period
        time_period_end: End of the analysis period
    """
    
    total_count: int = 0
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    average_rating: Optional[float] = None
    satisfaction_rate: float = 0.0
    type_distribution: Dict[str, int] = field(default_factory=dict)
    tag_distribution: Dict[str, int] = field(default_factory=dict)
    provider_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    lane_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    time_period_start: Optional[datetime] = None
    time_period_end: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_count": self.total_count,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "neutral_count": self.neutral_count,
            "average_rating": self.average_rating,
            "satisfaction_rate": round(self.satisfaction_rate, 2),
            "type_distribution": self.type_distribution,
            "tag_distribution": self.tag_distribution,
            "provider_stats": self.provider_stats,
            "lane_stats": self.lane_stats,
            "time_period_start": self.time_period_start.isoformat() if self.time_period_start else None,
            "time_period_end": self.time_period_end.isoformat() if self.time_period_end else None,
        }


@dataclass
class FeedbackTrend:
    """
    Feedback trends over time.
    """
    
    period: str  # "daily", "weekly", "monthly"
    data_points: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period,
            "data_points": self.data_points,
        }
