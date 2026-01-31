"""
Feedback Repository - SQLite-based storage for feedback data.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator
from uuid import UUID

from bifrost.feedback.models import Feedback, FeedbackType, FeedbackStats, FeedbackTrend
from bifrost.logger import logger


class FeedbackRepository:
    """
    SQLite repository for feedback storage and retrieval.
    
    Thread-safe with connection pooling for concurrent access.
    """
    
    _instance: Optional["FeedbackRepository"] = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: Optional[str] = None) -> "FeedbackRepository":
        """Singleton pattern for shared database access."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return
        
        self._db_path = db_path or str(Path.home() / ".bifrost" / "feedback.db")
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._local = threading.local()
        self._init_db()
        self._initialized = True
        
        logger.info("feedback_repository_initialized", db_path=self._db_path)
    
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
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    job_id TEXT,
                    feedback_type TEXT NOT NULL,
                    rating INTEGER,
                    comment TEXT,
                    tags TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    is_positive INTEGER,
                    is_negative INTEGER,
                    created_at TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_feedback_request_id 
                    ON feedback(request_id);
                CREATE INDEX IF NOT EXISTS idx_feedback_job_id 
                    ON feedback(job_id);
                CREATE INDEX IF NOT EXISTS idx_feedback_created_at 
                    ON feedback(created_at);
                CREATE INDEX IF NOT EXISTS idx_feedback_type 
                    ON feedback(feedback_type);
                CREATE INDEX IF NOT EXISTS idx_feedback_session 
                    ON feedback(session_id);
            """)
            conn.commit()
    
    def save(self, feedback: Feedback) -> Feedback:
        """Save feedback to database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO feedback 
                (id, request_id, job_id, feedback_type, rating, comment, 
                 tags, user_id, session_id, metadata, is_positive, is_negative, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(feedback.id),
                    feedback.request_id,
                    feedback.job_id,
                    feedback.feedback_type.value,
                    feedback.rating,
                    feedback.comment,
                    json.dumps(feedback.tags),
                    feedback.user_id,
                    feedback.session_id,
                    json.dumps(feedback.metadata),
                    1 if feedback.is_positive() else 0,
                    1 if feedback.is_negative() else 0,
                    feedback.created_at.isoformat(),
                ),
            )
            conn.commit()
        
        logger.info(
            "feedback_saved",
            feedback_id=str(feedback.id),
            request_id=feedback.request_id,
            feedback_type=feedback.feedback_type.value,
            is_positive=feedback.is_positive(),
        )
        
        return feedback
    
    def get_by_id(self, feedback_id: UUID) -> Optional[Feedback]:
        """Get feedback by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM feedback WHERE id = ?",
                (str(feedback_id),),
            ).fetchone()
        
        return self._row_to_feedback(row) if row else None
    
    def get_by_request_id(self, request_id: str) -> List[Feedback]:
        """Get all feedback for a specific request."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM feedback WHERE request_id = ? ORDER BY created_at DESC",
                (request_id,),
            ).fetchall()
        
        return [self._row_to_feedback(row) for row in rows]
    
    def get_by_job_id(self, job_id: str) -> List[Feedback]:
        """Get all feedback for a specific Heimdall job."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM feedback WHERE job_id = ? ORDER BY created_at DESC",
                (job_id,),
            ).fetchall()
        
        return [self._row_to_feedback(row) for row in rows]
    
    def get_recent(
        self,
        hours: int = 24,
        limit: int = 100,
        feedback_type: Optional[FeedbackType] = None,
    ) -> List[Feedback]:
        """Get recent feedback entries."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        with self._get_connection() as conn:
            if feedback_type:
                rows = conn.execute(
                    """
                    SELECT * FROM feedback 
                    WHERE created_at >= ? AND feedback_type = ?
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (since.isoformat(), feedback_type.value, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM feedback 
                    WHERE created_at >= ?
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (since.isoformat(), limit),
                ).fetchall()
        
        return [self._row_to_feedback(row) for row in rows]
    
    def get_negative_feedback(self, hours: int = 24, limit: int = 50) -> List[Feedback]:
        """Get recent negative feedback for review."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM feedback 
                WHERE created_at >= ? AND is_negative = 1
                ORDER BY created_at DESC LIMIT ?
                """,
                (since.isoformat(), limit),
            ).fetchall()
        
        return [self._row_to_feedback(row) for row in rows]
    
    def get_stats(
        self,
        hours: int = 24,
        provider: Optional[str] = None,
        lane: Optional[str] = None,
    ) -> FeedbackStats:
        """Calculate feedback statistics for a time period."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        now = datetime.now(timezone.utc)
        
        with self._get_connection() as conn:
            # Base query with optional filters
            base_condition = "created_at >= ?"
            params: List[Any] = [since.isoformat()]
            
            if provider:
                base_condition += " AND json_extract(metadata, '$.provider') = ?"
                params.append(provider)
            if lane:
                base_condition += " AND json_extract(metadata, '$.lane') = ?"
                params.append(lane)
            
            # Total counts
            row = conn.execute(
                f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(is_positive) as positive,
                    SUM(is_negative) as negative,
                    AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating
                FROM feedback
                WHERE {base_condition}
                """,
                params,
            ).fetchone()
            
            total = row["total"] or 0
            positive = row["positive"] or 0
            negative = row["negative"] or 0
            avg_rating = row["avg_rating"]
            
            # Type distribution
            type_rows = conn.execute(
                f"""
                SELECT feedback_type, COUNT(*) as count
                FROM feedback
                WHERE {base_condition}
                GROUP BY feedback_type
                """,
                params,
            ).fetchall()
            type_dist = {r["feedback_type"]: r["count"] for r in type_rows}
            
            # Provider stats
            provider_rows = conn.execute(
                f"""
                SELECT 
                    json_extract(metadata, '$.provider') as provider,
                    COUNT(*) as total,
                    SUM(is_positive) as positive,
                    AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating
                FROM feedback
                WHERE {base_condition} AND provider IS NOT NULL
                GROUP BY provider
                """,
                params,
            ).fetchall()
            provider_stats = {
                r["provider"]: {
                    "total": r["total"],
                    "positive": r["positive"] or 0,
                    "satisfaction_rate": round((r["positive"] or 0) / r["total"] * 100, 1) if r["total"] > 0 else 0,
                    "avg_rating": round(r["avg_rating"], 2) if r["avg_rating"] else None,
                }
                for r in provider_rows if r["provider"]
            }
            
            # Lane stats
            lane_rows = conn.execute(
                f"""
                SELECT 
                    json_extract(metadata, '$.lane') as lane,
                    COUNT(*) as total,
                    SUM(is_positive) as positive,
                    AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating
                FROM feedback
                WHERE {base_condition} AND lane IS NOT NULL
                GROUP BY lane
                """,
                params,
            ).fetchall()
            lane_stats = {
                r["lane"]: {
                    "total": r["total"],
                    "positive": r["positive"] or 0,
                    "satisfaction_rate": round((r["positive"] or 0) / r["total"] * 100, 1) if r["total"] > 0 else 0,
                    "avg_rating": round(r["avg_rating"], 2) if r["avg_rating"] else None,
                }
                for r in lane_rows if r["lane"]
            }
        
        satisfaction_rate = (positive / total * 100) if total > 0 else 0.0
        
        return FeedbackStats(
            total_count=total,
            positive_count=positive,
            negative_count=negative,
            neutral_count=total - positive - negative,
            average_rating=round(avg_rating, 2) if avg_rating else None,
            satisfaction_rate=satisfaction_rate,
            type_distribution=type_dist,
            provider_stats=provider_stats,
            lane_stats=lane_stats,
            time_period_start=since,
            time_period_end=now,
        )
    
    def get_trends(self, days: int = 7) -> FeedbackTrend:
        """Get daily feedback trends."""
        data_points = []
        
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total,
                    SUM(is_positive) as positive,
                    SUM(is_negative) as negative,
                    AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating
                FROM feedback
                WHERE created_at >= DATE('now', ?)
                GROUP BY DATE(created_at)
                ORDER BY date
                """,
                (f"-{days} days",),
            ).fetchall()
            
            for row in rows:
                total = row["total"]
                positive = row["positive"] or 0
                data_points.append({
                    "date": row["date"],
                    "total": total,
                    "positive": positive,
                    "negative": row["negative"] or 0,
                    "satisfaction_rate": round(positive / total * 100, 1) if total > 0 else 0,
                    "avg_rating": round(row["avg_rating"], 2) if row["avg_rating"] else None,
                })
        
        return FeedbackTrend(period="daily", data_points=data_points)
    
    def _row_to_feedback(self, row: sqlite3.Row) -> Feedback:
        """Convert database row to Feedback object."""
        return Feedback(
            id=UUID(row["id"]),
            request_id=row["request_id"],
            job_id=row["job_id"],
            feedback_type=FeedbackType(row["feedback_type"]),
            rating=row["rating"],
            comment=row["comment"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            user_id=row["user_id"],
            session_id=row["session_id"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=datetime.fromisoformat(row["created_at"]),
        )
    
    def delete_old(self, days: int = 90) -> int:
        """Delete feedback older than specified days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM feedback WHERE created_at < ?",
                (cutoff.isoformat(),),
            )
            conn.commit()
            deleted = cursor.rowcount
        
        logger.info("feedback_cleanup", deleted_count=deleted, older_than_days=days)
        return deleted


# Global instance getter
def get_feedback_repository() -> FeedbackRepository:
    """Get the singleton feedback repository instance."""
    return FeedbackRepository()
