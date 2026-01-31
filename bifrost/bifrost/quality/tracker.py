"""
Quality Tracker - Stores and aggregates quality metrics over time.
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

from bifrost.quality.models import (
    QualityScore,
    QualityDimension,
    AnalysisQualityReport,
    QualityTrend,
)
from bifrost.logger import logger


class QualityTracker:
    """
    Tracks and stores quality metrics over time.
    
    Provides:
    - Report storage and retrieval
    - Aggregated statistics
    - Trend analysis
    - Alerting on quality degradation
    """
    
    _instance: Optional["QualityTracker"] = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: Optional[str] = None) -> "QualityTracker":
        """Singleton pattern."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return
        
        self._db_path = db_path or str(Path.home() / ".bifrost" / "quality.db")
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._local = threading.local()
        self._init_db()
        self._initialized = True
        
        logger.info("quality_tracker_initialized", db_path=self._db_path)
    
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
                CREATE TABLE IF NOT EXISTS quality_reports (
                    id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    job_id TEXT,
                    overall_score REAL NOT NULL,
                    overall_grade TEXT NOT NULL,
                    scores TEXT NOT NULL,
                    provider TEXT,
                    lane TEXT,
                    model TEXT,
                    latency_ms INTEGER,
                    token_count INTEGER,
                    analyzed_at TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_quality_request_id 
                    ON quality_reports(request_id);
                CREATE INDEX IF NOT EXISTS idx_quality_analyzed_at 
                    ON quality_reports(analyzed_at);
                CREATE INDEX IF NOT EXISTS idx_quality_provider 
                    ON quality_reports(provider);
                CREATE INDEX IF NOT EXISTS idx_quality_grade 
                    ON quality_reports(overall_grade);
            """)
            conn.commit()
    
    def save_report(self, report: AnalysisQualityReport) -> AnalysisQualityReport:
        """Save a quality report."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO quality_reports 
                (id, request_id, job_id, overall_score, overall_grade, scores,
                 provider, lane, model, latency_ms, token_count, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(report.id),
                    report.request_id,
                    report.job_id,
                    report.overall_score,
                    report.overall_grade,
                    json.dumps([s.to_dict() for s in report.scores]),
                    report.provider,
                    report.lane,
                    report.model,
                    report.latency_ms,
                    report.token_count,
                    report.analyzed_at.isoformat(),
                ),
            )
            conn.commit()
        
        logger.info(
            "quality_report_saved",
            report_id=str(report.id),
            overall_score=report.overall_score,
            provider=report.provider,
        )
        
        return report
    
    def get_report(self, report_id: UUID) -> Optional[AnalysisQualityReport]:
        """Get a specific report by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM quality_reports WHERE id = ?",
                (str(report_id),),
            ).fetchone()
        
        return self._row_to_report(row) if row else None
    
    def get_reports_for_request(self, request_id: str) -> List[AnalysisQualityReport]:
        """Get all reports for a request."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM quality_reports WHERE request_id = ?",
                (request_id,),
            ).fetchall()
        
        return [self._row_to_report(row) for row in rows]
    
    def get_recent_reports(
        self,
        hours: int = 24,
        limit: int = 100,
        provider: Optional[str] = None,
        min_grade: Optional[str] = None,
    ) -> List[AnalysisQualityReport]:
        """Get recent quality reports."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = "SELECT * FROM quality_reports WHERE analyzed_at >= ?"
        params: List[Any] = [since.isoformat()]
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        if min_grade:
            grade_order = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}
            min_grade_value = grade_order.get(min_grade, 0)
            query += f" AND overall_grade IN ({','.join(['?' for g in grade_order if grade_order[g] >= min_grade_value])})"
            params.extend([g for g in grade_order if grade_order[g] >= min_grade_value])
        
        query += " ORDER BY analyzed_at DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        
        return [self._row_to_report(row) for row in rows]
    
    def get_stats(
        self,
        hours: int = 24,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get aggregated quality statistics."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        with self._get_connection() as conn:
            base_query = "analyzed_at >= ?"
            params: List[Any] = [since.isoformat()]
            
            if provider:
                base_query += " AND provider = ?"
                params.append(provider)
            
            # Overall stats
            row = conn.execute(
                f"""
                SELECT 
                    COUNT(*) as total,
                    AVG(overall_score) as avg_score,
                    MIN(overall_score) as min_score,
                    MAX(overall_score) as max_score,
                    AVG(latency_ms) as avg_latency
                FROM quality_reports
                WHERE {base_query}
                """,
                params,
            ).fetchone()
            
            # Grade distribution
            grade_rows = conn.execute(
                f"""
                SELECT overall_grade, COUNT(*) as count
                FROM quality_reports
                WHERE {base_query}
                GROUP BY overall_grade
                """,
                params,
            ).fetchall()
            grade_dist = {r["overall_grade"]: r["count"] for r in grade_rows}
            
            # Provider stats
            provider_rows = conn.execute(
                f"""
                SELECT provider, AVG(overall_score) as avg_score, COUNT(*) as count
                FROM quality_reports
                WHERE {base_query} AND provider IS NOT NULL
                GROUP BY provider
                """,
                params,
            ).fetchall()
            provider_stats = {
                r["provider"]: {
                    "avg_score": round(r["avg_score"], 3),
                    "count": r["count"],
                }
                for r in provider_rows
            }
        
        return {
            "period_hours": hours,
            "total_reports": row["total"],
            "average_score": round(row["avg_score"], 3) if row["avg_score"] else None,
            "min_score": round(row["min_score"], 3) if row["min_score"] else None,
            "max_score": round(row["max_score"], 3) if row["max_score"] else None,
            "average_latency_ms": round(row["avg_latency"]) if row["avg_latency"] else None,
            "grade_distribution": grade_dist,
            "by_provider": provider_stats,
        }
    
    def get_dimension_stats(
        self,
        hours: int = 24,
        dimension: Optional[QualityDimension] = None,
    ) -> Dict[str, Any]:
        """Get statistics for specific quality dimensions."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT scores FROM quality_reports
                WHERE analyzed_at >= ?
                """,
                (since.isoformat(),),
            ).fetchall()
        
        dimension_scores: Dict[str, List[float]] = {}
        
        for row in rows:
            scores = json.loads(row["scores"])
            for score_data in scores:
                dim = score_data["dimension"]
                if dimension and dim != dimension.value:
                    continue
                if dim not in dimension_scores:
                    dimension_scores[dim] = []
                dimension_scores[dim].append(score_data["score"])
        
        result = {}
        for dim, scores in dimension_scores.items():
            if scores:
                result[dim] = {
                    "count": len(scores),
                    "average": round(sum(scores) / len(scores), 3),
                    "min": round(min(scores), 3),
                    "max": round(max(scores), 3),
                }
        
        return {
            "period_hours": hours,
            "dimensions": result,
        }
    
    def get_trends(self, days: int = 7) -> QualityTrend:
        """Get daily quality trends."""
        data_points = []
        
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT 
                    DATE(analyzed_at) as date,
                    COUNT(*) as total,
                    AVG(overall_score) as avg_score,
                    MIN(overall_score) as min_score,
                    MAX(overall_score) as max_score
                FROM quality_reports
                WHERE analyzed_at >= DATE('now', ?)
                GROUP BY DATE(analyzed_at)
                ORDER BY date
                """,
                (f"-{days} days",),
            ).fetchall()
            
            for row in rows:
                data_points.append({
                    "date": row["date"],
                    "total": row["total"],
                    "avg_score": round(row["avg_score"], 3) if row["avg_score"] else None,
                    "min_score": round(row["min_score"], 3) if row["min_score"] else None,
                    "max_score": round(row["max_score"], 3) if row["max_score"] else None,
                })
        
        return QualityTrend(period="daily", data_points=data_points)
    
    def get_low_quality_reports(
        self,
        hours: int = 24,
        threshold: float = 0.6,
        limit: int = 50,
    ) -> List[AnalysisQualityReport]:
        """Get reports with quality below threshold."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM quality_reports
                WHERE analyzed_at >= ? AND overall_score < ?
                ORDER BY overall_score ASC
                LIMIT ?
                """,
                (since.isoformat(), threshold, limit),
            ).fetchall()
        
        return [self._row_to_report(row) for row in rows]
    
    def _row_to_report(self, row: sqlite3.Row) -> AnalysisQualityReport:
        """Convert database row to report object."""
        scores_data = json.loads(row["scores"])
        scores = []
        for s in scores_data:
            scores.append(QualityScore(
                dimension=QualityDimension(s["dimension"]),
                score=s["score"],
                weight=s.get("weight", 1.0),
                details=s.get("details"),
                factors=s.get("factors", {}),
            ))
        
        return AnalysisQualityReport(
            id=UUID(row["id"]),
            request_id=row["request_id"],
            job_id=row["job_id"],
            scores=scores,
            overall_score=row["overall_score"],
            overall_grade=row["overall_grade"],
            provider=row["provider"],
            lane=row["lane"],
            model=row["model"],
            latency_ms=row["latency_ms"],
            token_count=row["token_count"],
            analyzed_at=datetime.fromisoformat(row["analyzed_at"]),
        )
    
    def cleanup_old(self, days: int = 30) -> int:
        """Delete reports older than specified days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM quality_reports WHERE analyzed_at < ?",
                (cutoff.isoformat(),),
            )
            conn.commit()
            deleted = cursor.rowcount
        
        logger.info("quality_reports_cleanup", deleted_count=deleted, older_than_days=days)
        return deleted


# Global tracker getter
def get_quality_tracker() -> QualityTracker:
    """Get the singleton quality tracker instance."""
    return QualityTracker()
