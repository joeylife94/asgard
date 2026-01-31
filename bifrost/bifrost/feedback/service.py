"""
Feedback Service - Business logic for feedback management.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from bifrost.feedback.models import (
    Feedback,
    FeedbackType,
    FeedbackStats,
    FeedbackTrend,
)
from bifrost.feedback.repository import FeedbackRepository, get_feedback_repository
from bifrost.logger import logger


class FeedbackService:
    """
    Service layer for feedback operations.
    
    Provides business logic for collecting, analyzing, and
    acting on user feedback for AI analysis quality.
    """
    
    def __init__(self, repository: Optional[FeedbackRepository] = None):
        self.repository = repository or get_feedback_repository()
    
    def submit_feedback(
        self,
        request_id: str,
        feedback_type: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        tags: Optional[List[str]] = None,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """
        Submit user feedback for an analysis response.
        
        Args:
            request_id: The analysis request ID
            feedback_type: Type of feedback (thumbs_up, thumbs_down, rating, etc.)
            rating: Optional star rating (1-5)
            comment: Optional user comment
            tags: Optional categorization tags
            job_id: Associated Heimdall job ID
            user_id: Anonymous user identifier
            session_id: Browser session ID
            metadata: Additional context (provider, lane, latency, etc.)
        
        Returns:
            Created Feedback object
        """
        # Validate feedback type
        try:
            fb_type = FeedbackType(feedback_type)
        except ValueError:
            fb_type = FeedbackType.RATING if rating else FeedbackType.THUMBS_UP
        
        # Validate rating
        if rating is not None:
            rating = max(1, min(5, rating))
        
        # Sanitize comment
        if comment:
            comment = comment.strip()[:2000]  # Max 2000 chars
        
        feedback = Feedback(
            id=uuid4(),
            request_id=request_id,
            job_id=job_id,
            feedback_type=fb_type,
            rating=rating,
            comment=comment,
            tags=tags or [],
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )
        
        saved = self.repository.save(feedback)
        
        # Log for analytics
        logger.info(
            "feedback_submitted",
            feedback_id=str(saved.id),
            request_id=request_id,
            job_id=job_id,
            feedback_type=fb_type.value,
            rating=rating,
            is_positive=saved.is_positive(),
            is_negative=saved.is_negative(),
            provider=metadata.get("provider") if metadata else None,
            lane=metadata.get("lane") if metadata else None,
        )
        
        # Trigger alerts for negative feedback with comments
        if saved.is_negative() and comment:
            self._handle_negative_feedback(saved)
        
        return saved
    
    def submit_quick_feedback(
        self,
        request_id: str,
        is_positive: bool,
        job_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """
        Submit quick thumbs up/down feedback.
        
        Convenience method for simple binary feedback.
        """
        return self.submit_feedback(
            request_id=request_id,
            feedback_type=FeedbackType.THUMBS_UP.value if is_positive else FeedbackType.THUMBS_DOWN.value,
            job_id=job_id,
            session_id=session_id,
            metadata=metadata,
        )
    
    def get_feedback(self, feedback_id: UUID) -> Optional[Feedback]:
        """Get feedback by ID."""
        return self.repository.get_by_id(feedback_id)
    
    def get_feedback_for_request(self, request_id: str) -> List[Feedback]:
        """Get all feedback for a specific request."""
        return self.repository.get_by_request_id(request_id)
    
    def get_feedback_for_job(self, job_id: str) -> List[Feedback]:
        """Get all feedback for a Heimdall job."""
        return self.repository.get_by_job_id(job_id)
    
    def get_recent_feedback(
        self,
        hours: int = 24,
        limit: int = 100,
        feedback_type: Optional[str] = None,
    ) -> List[Feedback]:
        """Get recent feedback entries."""
        fb_type = FeedbackType(feedback_type) if feedback_type else None
        return self.repository.get_recent(hours=hours, limit=limit, feedback_type=fb_type)
    
    def get_negative_feedback(self, hours: int = 24, limit: int = 50) -> List[Feedback]:
        """Get recent negative feedback for review."""
        return self.repository.get_negative_feedback(hours=hours, limit=limit)
    
    def get_stats(
        self,
        hours: int = 24,
        provider: Optional[str] = None,
        lane: Optional[str] = None,
    ) -> FeedbackStats:
        """Get aggregated feedback statistics."""
        return self.repository.get_stats(hours=hours, provider=provider, lane=lane)
    
    def get_trends(self, days: int = 7) -> FeedbackTrend:
        """Get feedback trends over time."""
        return self.repository.get_trends(days=days)
    
    def get_satisfaction_score(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate overall satisfaction score.
        
        Returns a comprehensive satisfaction analysis including
        scores by provider and lane.
        """
        stats = self.get_stats(hours=hours)
        
        # Calculate NPS-like score
        # Positive = Promoters, Negative = Detractors
        if stats.total_count > 0:
            nps_score = ((stats.positive_count - stats.negative_count) / stats.total_count) * 100
        else:
            nps_score = 0
        
        return {
            "overall_satisfaction_rate": round(stats.satisfaction_rate, 1),
            "nps_score": round(nps_score, 1),
            "average_rating": stats.average_rating,
            "total_feedback": stats.total_count,
            "positive_feedback": stats.positive_count,
            "negative_feedback": stats.negative_count,
            "by_provider": stats.provider_stats,
            "by_lane": stats.lane_stats,
            "time_period_hours": hours,
        }
    
    def _handle_negative_feedback(self, feedback: Feedback) -> None:
        """
        Handle negative feedback with potential alerting.
        
        Could be extended to:
        - Send Slack notifications
        - Create support tickets
        - Trigger model retraining
        """
        logger.warning(
            "negative_feedback_with_comment",
            feedback_id=str(feedback.id),
            request_id=feedback.request_id,
            feedback_type=feedback.feedback_type.value,
            comment_preview=feedback.comment[:100] if feedback.comment else None,
            provider=feedback.metadata.get("provider"),
            lane=feedback.metadata.get("lane"),
        )
        
        # TODO: Integrate with Slack notifier for critical feedback
        # if feedback.rating and feedback.rating <= 1:
        #     slack.send_alert(...)
    
    def cleanup_old_feedback(self, days: int = 90) -> int:
        """Delete feedback older than specified days."""
        return self.repository.delete_old(days=days)


# Global service getter
_service_instance: Optional[FeedbackService] = None


def get_feedback_service() -> FeedbackService:
    """Get the singleton feedback service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = FeedbackService()
    return _service_instance
