"""
Tests for Feedback System.
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from bifrost.feedback.models import (
    Feedback,
    FeedbackType,
    FeedbackRating,
    FeedbackStats,
)
from bifrost.feedback.repository import FeedbackRepository
from bifrost.feedback.service import FeedbackService


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Reset singleton for testing
    FeedbackRepository._instance = None
    
    yield path
    
    # Cleanup
    FeedbackRepository._instance = None
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def repository(temp_db):
    """Create a repository with temp database."""
    return FeedbackRepository(db_path=temp_db)


@pytest.fixture
def service(repository):
    """Create a service with the test repository."""
    return FeedbackService(repository=repository)


class TestFeedbackModel:
    """Tests for Feedback model."""

    def test_feedback_creation(self):
        feedback = Feedback(
            request_id="req-123",
            feedback_type=FeedbackType.THUMBS_UP,
        )
        
        assert feedback.request_id == "req-123"
        assert feedback.feedback_type == FeedbackType.THUMBS_UP
        assert feedback.id is not None

    def test_is_positive_thumbs_up(self):
        feedback = Feedback(feedback_type=FeedbackType.THUMBS_UP)
        assert feedback.is_positive()
        assert not feedback.is_negative()

    def test_is_positive_high_rating(self):
        feedback = Feedback(feedback_type=FeedbackType.RATING, rating=5)
        assert feedback.is_positive()

    def test_is_negative_thumbs_down(self):
        feedback = Feedback(feedback_type=FeedbackType.THUMBS_DOWN)
        assert feedback.is_negative()
        assert not feedback.is_positive()

    def test_is_negative_low_rating(self):
        feedback = Feedback(feedback_type=FeedbackType.RATING, rating=1)
        assert feedback.is_negative()

    def test_is_negative_issue_types(self):
        for fb_type in [FeedbackType.INACCURATE, FeedbackType.INCOMPLETE, FeedbackType.IRRELEVANT]:
            feedback = Feedback(feedback_type=fb_type)
            assert feedback.is_negative()

    def test_to_dict(self):
        feedback = Feedback(
            request_id="req-123",
            feedback_type=FeedbackType.RATING,
            rating=4,
            comment="Great response!",
            tags=["helpful"],
        )
        
        data = feedback.to_dict()
        
        assert data["request_id"] == "req-123"
        assert data["feedback_type"] == "rating"
        assert data["rating"] == 4
        assert data["comment"] == "Great response!"
        assert data["tags"] == ["helpful"]
        assert data["is_positive"] is True

    def test_from_dict(self):
        data = {
            "id": str(uuid4()),
            "request_id": "req-456",
            "feedback_type": "thumbs_down",
            "rating": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        feedback = Feedback.from_dict(data)
        
        assert feedback.request_id == "req-456"
        assert feedback.feedback_type == FeedbackType.THUMBS_DOWN
        assert feedback.rating == 2


class TestFeedbackRepository:
    """Tests for FeedbackRepository."""

    def test_save_and_retrieve(self, repository):
        feedback = Feedback(
            request_id="req-001",
            feedback_type=FeedbackType.THUMBS_UP,
            comment="Works great!",
        )
        
        saved = repository.save(feedback)
        retrieved = repository.get_by_id(saved.id)
        
        assert retrieved is not None
        assert retrieved.request_id == "req-001"
        assert retrieved.comment == "Works great!"

    def test_get_by_request_id(self, repository):
        # Save multiple feedbacks for same request
        for i in range(3):
            repository.save(Feedback(
                request_id="req-multi",
                feedback_type=FeedbackType.THUMBS_UP if i % 2 == 0 else FeedbackType.THUMBS_DOWN,
            ))
        
        feedbacks = repository.get_by_request_id("req-multi")
        assert len(feedbacks) == 3

    def test_get_by_job_id(self, repository):
        repository.save(Feedback(
            request_id="req-job",
            job_id="job-123",
            feedback_type=FeedbackType.RATING,
            rating=5,
        ))
        
        feedbacks = repository.get_by_job_id("job-123")
        assert len(feedbacks) == 1
        assert feedbacks[0].rating == 5

    def test_get_recent(self, repository):
        # Save some feedback
        for i in range(5):
            repository.save(Feedback(
                request_id=f"req-recent-{i}",
                feedback_type=FeedbackType.THUMBS_UP,
            ))
        
        recent = repository.get_recent(hours=1, limit=10)
        assert len(recent) == 5

    def test_get_negative_feedback(self, repository):
        # Mix of positive and negative
        repository.save(Feedback(request_id="pos", feedback_type=FeedbackType.THUMBS_UP))
        repository.save(Feedback(request_id="neg1", feedback_type=FeedbackType.THUMBS_DOWN))
        repository.save(Feedback(request_id="neg2", feedback_type=FeedbackType.INACCURATE))
        
        negative = repository.get_negative_feedback(hours=1)
        assert len(negative) == 2

    def test_get_stats(self, repository):
        # Create test data
        repository.save(Feedback(request_id="s1", feedback_type=FeedbackType.THUMBS_UP))
        repository.save(Feedback(request_id="s2", feedback_type=FeedbackType.THUMBS_UP))
        repository.save(Feedback(request_id="s3", feedback_type=FeedbackType.THUMBS_DOWN))
        repository.save(Feedback(request_id="s4", feedback_type=FeedbackType.RATING, rating=4))
        repository.save(Feedback(request_id="s5", feedback_type=FeedbackType.RATING, rating=5))
        
        stats = repository.get_stats(hours=1)
        
        assert stats.total_count == 5
        assert stats.positive_count == 4  # 2 thumbs up + 2 high ratings
        assert stats.negative_count == 1
        assert stats.average_rating == 4.5

    def test_get_stats_by_provider(self, repository):
        repository.save(Feedback(
            request_id="p1",
            feedback_type=FeedbackType.THUMBS_UP,
            metadata={"provider": "ollama"},
        ))
        repository.save(Feedback(
            request_id="p2",
            feedback_type=FeedbackType.THUMBS_UP,
            metadata={"provider": "ollama"},
        ))
        repository.save(Feedback(
            request_id="p3",
            feedback_type=FeedbackType.THUMBS_DOWN,
            metadata={"provider": "bedrock"},
        ))
        
        stats = repository.get_stats(hours=1)
        
        assert "ollama" in stats.provider_stats
        assert stats.provider_stats["ollama"]["total"] == 2
        assert stats.provider_stats["ollama"]["satisfaction_rate"] == 100.0


class TestFeedbackService:
    """Tests for FeedbackService."""

    def test_submit_feedback(self, service):
        feedback = service.submit_feedback(
            request_id="svc-001",
            feedback_type="thumbs_up",
            comment="Very helpful!",
        )
        
        assert feedback.request_id == "svc-001"
        assert feedback.feedback_type == FeedbackType.THUMBS_UP
        assert feedback.comment == "Very helpful!"

    def test_submit_feedback_with_rating(self, service):
        feedback = service.submit_feedback(
            request_id="svc-002",
            feedback_type="rating",
            rating=5,
            metadata={"provider": "ollama", "lane": "on_device_rag"},
        )
        
        assert feedback.rating == 5
        assert feedback.metadata["provider"] == "ollama"

    def test_submit_quick_feedback_positive(self, service):
        feedback = service.submit_quick_feedback(
            request_id="quick-001",
            is_positive=True,
        )
        
        assert feedback.feedback_type == FeedbackType.THUMBS_UP
        assert feedback.is_positive()

    def test_submit_quick_feedback_negative(self, service):
        feedback = service.submit_quick_feedback(
            request_id="quick-002",
            is_positive=False,
        )
        
        assert feedback.feedback_type == FeedbackType.THUMBS_DOWN
        assert feedback.is_negative()

    def test_get_satisfaction_score(self, service):
        # Create test data
        for _ in range(7):
            service.submit_quick_feedback("sat-test", is_positive=True)
        for _ in range(3):
            service.submit_quick_feedback("sat-test", is_positive=False)
        
        score = service.get_satisfaction_score(hours=1)
        
        assert score["total_feedback"] == 10
        assert score["positive_feedback"] == 7
        assert score["negative_feedback"] == 3
        assert score["overall_satisfaction_rate"] == 70.0
        # NPS = (7 - 3) / 10 * 100 = 40
        assert score["nps_score"] == 40.0

    def test_rating_clamping(self, service):
        # Rating should be clamped to 1-5
        feedback = service.submit_feedback(
            request_id="clamp-test",
            feedback_type="rating",
            rating=10,  # Too high
        )
        assert feedback.rating == 5
        
        feedback2 = service.submit_feedback(
            request_id="clamp-test2",
            feedback_type="rating",
            rating=0,  # Too low
        )
        assert feedback2.rating == 1

    def test_comment_truncation(self, service):
        long_comment = "x" * 3000  # Over 2000 limit
        feedback = service.submit_feedback(
            request_id="truncate-test",
            feedback_type="thumbs_up",
            comment=long_comment,
        )
        assert len(feedback.comment) == 2000

    def test_get_feedback_for_request(self, service):
        service.submit_feedback("multi-req", "thumbs_up")
        service.submit_feedback("multi-req", "rating", rating=4)
        
        feedbacks = service.get_feedback_for_request("multi-req")
        assert len(feedbacks) == 2

    def test_get_trends(self, service):
        # Add some feedback
        for _ in range(3):
            service.submit_quick_feedback("trend-test", is_positive=True)
        
        trends = service.get_trends(days=7)
        
        assert trends.period == "daily"
        assert len(trends.data_points) > 0


class TestFeedbackStats:
    """Tests for FeedbackStats."""

    def test_stats_to_dict(self):
        stats = FeedbackStats(
            total_count=100,
            positive_count=75,
            negative_count=15,
            neutral_count=10,
            average_rating=4.2,
            satisfaction_rate=75.0,
        )
        
        data = stats.to_dict()
        
        assert data["total_count"] == 100
        assert data["satisfaction_rate"] == 75.0
        assert data["average_rating"] == 4.2
