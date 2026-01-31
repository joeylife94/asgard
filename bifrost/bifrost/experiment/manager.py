"""
Experiment Manager - Manages A/B test lifecycle and assignments.
"""

from __future__ import annotations

import hashlib
import json
import random
import sqlite3
import threading
import statistics
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator, Tuple
from uuid import UUID

from bifrost.experiment.models import (
    Experiment,
    Variant,
    VariantType,
    ExperimentStatus,
    ExperimentResult,
    ExperimentAssignment,
    VariantMetrics,
    StatisticalResult,
)
from bifrost.logger import logger


class ExperimentManager:
    """
    Manages A/B test experiments.
    
    Responsibilities:
    - Experiment CRUD operations
    - Traffic assignment
    - Metrics collection
    - Statistical analysis
    """
    
    _instance: Optional["ExperimentManager"] = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: Optional[str] = None) -> "ExperimentManager":
        """Singleton pattern."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return
        
        self._db_path = db_path or str(Path.home() / ".bifrost" / "experiments.db")
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._local = threading.local()
        self._init_db()
        self._initialized = True
        
        # Cache for active experiments
        self._active_experiments: Dict[UUID, Experiment] = {}
        
        logger.info("experiment_manager_initialized", db_path=self._db_path)
    
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
                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    data TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    ended_at TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_exp_status 
                    ON experiments(status);
                CREATE INDEX IF NOT EXISTS idx_exp_name 
                    ON experiments(name);
                
                CREATE TABLE IF NOT EXISTS assignments (
                    id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    variant_name TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    assigned_at TEXT NOT NULL,
                    quality_score REAL,
                    latency_ms INTEGER,
                    satisfaction_score REAL,
                    error_occurred INTEGER DEFAULT 0,
                    token_count INTEGER,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_assign_exp 
                    ON assignments(experiment_id);
                CREATE INDEX IF NOT EXISTS idx_assign_variant 
                    ON assignments(experiment_id, variant_name);
                CREATE INDEX IF NOT EXISTS idx_assign_request 
                    ON assignments(request_id);
            """)
            conn.commit()
    
    # ==================== Experiment CRUD ====================
    
    def create_experiment(self, experiment: Experiment) -> Experiment:
        """Create a new experiment."""
        errors = experiment.validate()
        if errors:
            raise ValueError(f"Invalid experiment: {', '.join(errors)}")
        
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO experiments (id, name, description, data, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(experiment.id),
                    experiment.name,
                    experiment.description,
                    json.dumps(experiment.to_dict()),
                    experiment.status.value,
                    experiment.created_at.isoformat(),
                ),
            )
            conn.commit()
        
        logger.info(
            "experiment_created",
            experiment_id=str(experiment.id),
            name=experiment.name,
        )
        
        return experiment
    
    def get_experiment(self, experiment_id: UUID) -> Optional[Experiment]:
        """Get experiment by ID."""
        # Check cache first
        if experiment_id in self._active_experiments:
            return self._active_experiments[experiment_id]
        
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT data FROM experiments WHERE id = ?",
                (str(experiment_id),),
            ).fetchone()
        
        if not row:
            return None
        
        return Experiment.from_dict(json.loads(row["data"]))
    
    def get_experiment_by_name(self, name: str) -> Optional[Experiment]:
        """Get experiment by name."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT data FROM experiments WHERE name = ?",
                (name,),
            ).fetchone()
        
        if not row:
            return None
        
        return Experiment.from_dict(json.loads(row["data"]))
    
    def list_experiments(
        self,
        status: Optional[ExperimentStatus] = None,
        limit: int = 100,
    ) -> List[Experiment]:
        """List experiments with optional status filter."""
        with self._get_connection() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT data FROM experiments 
                    WHERE status = ? 
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (status.value, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT data FROM experiments ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        
        return [Experiment.from_dict(json.loads(row["data"])) for row in rows]
    
    def update_experiment(self, experiment: Experiment) -> Experiment:
        """Update an existing experiment."""
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE experiments 
                SET name = ?, description = ?, data = ?, status = ?,
                    started_at = ?, ended_at = ?
                WHERE id = ?
                """,
                (
                    experiment.name,
                    experiment.description,
                    json.dumps(experiment.to_dict()),
                    experiment.status.value,
                    experiment.started_at.isoformat() if experiment.started_at else None,
                    experiment.ended_at.isoformat() if experiment.ended_at else None,
                    str(experiment.id),
                ),
            )
            conn.commit()
        
        # Update cache if active
        if experiment.status == ExperimentStatus.RUNNING:
            self._active_experiments[experiment.id] = experiment
        elif experiment.id in self._active_experiments:
            del self._active_experiments[experiment.id]
        
        return experiment
    
    def delete_experiment(self, experiment_id: UUID) -> bool:
        """Delete an experiment and its assignments."""
        with self._get_connection() as conn:
            # Delete assignments first
            conn.execute(
                "DELETE FROM assignments WHERE experiment_id = ?",
                (str(experiment_id),),
            )
            
            cursor = conn.execute(
                "DELETE FROM experiments WHERE id = ?",
                (str(experiment_id),),
            )
            conn.commit()
            
            deleted = cursor.rowcount > 0
        
        if experiment_id in self._active_experiments:
            del self._active_experiments[experiment_id]
        
        return deleted
    
    # ==================== Experiment Lifecycle ====================
    
    def start_experiment(self, experiment_id: UUID) -> Experiment:
        """Start an experiment."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        if experiment.status not in [ExperimentStatus.DRAFT, ExperimentStatus.PAUSED]:
            raise ValueError(f"Cannot start experiment in {experiment.status} status")
        
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = experiment.started_at or datetime.now(timezone.utc)
        
        self.update_experiment(experiment)
        self._active_experiments[experiment.id] = experiment
        
        logger.info(
            "experiment_started",
            experiment_id=str(experiment_id),
            name=experiment.name,
        )
        
        return experiment
    
    def pause_experiment(self, experiment_id: UUID) -> Experiment:
        """Pause a running experiment."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        if experiment.status != ExperimentStatus.RUNNING:
            raise ValueError(f"Cannot pause experiment in {experiment.status} status")
        
        experiment.status = ExperimentStatus.PAUSED
        self.update_experiment(experiment)
        
        logger.info("experiment_paused", experiment_id=str(experiment_id))
        
        return experiment
    
    def stop_experiment(
        self,
        experiment_id: UUID,
        reason: str = "",
    ) -> Experiment:
        """Stop an experiment early."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment.status = ExperimentStatus.STOPPED
        experiment.ended_at = datetime.now(timezone.utc)
        
        self.update_experiment(experiment)
        
        logger.info(
            "experiment_stopped",
            experiment_id=str(experiment_id),
            reason=reason,
        )
        
        return experiment
    
    def complete_experiment(self, experiment_id: UUID) -> Experiment:
        """Mark an experiment as completed."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment.status = ExperimentStatus.COMPLETED
        experiment.ended_at = datetime.now(timezone.utc)
        
        self.update_experiment(experiment)
        
        logger.info("experiment_completed", experiment_id=str(experiment_id))
        
        return experiment
    
    # ==================== Traffic Assignment ====================
    
    def assign_variant(
        self,
        experiment_id: UUID,
        request_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Optional[Variant]:
        """
        Assign a request to a variant.
        
        Uses consistent hashing for deterministic assignments.
        """
        experiment = self._active_experiments.get(experiment_id)
        if not experiment:
            experiment = self.get_experiment(experiment_id)
            if not experiment or not experiment.is_active():
                return None
            self._active_experiments[experiment_id] = experiment
        
        # Check eligibility
        if not experiment.allocation.is_eligible(user_id=user_id, query=query):
            return None
        
        # Random sampling based on target_percentage
        if random.random() * 100 > experiment.allocation.target_percentage:
            return None
        
        # Consistent assignment based on user/request
        variant = self._select_variant(experiment, user_id or request_id)
        
        # Record assignment
        assignment = ExperimentAssignment(
            experiment_id=experiment.id,
            variant_name=variant.name,
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
        )
        self._save_assignment(assignment)
        
        logger.debug(
            "variant_assigned",
            experiment_id=str(experiment_id),
            variant=variant.name,
            request_id=request_id,
        )
        
        return variant
    
    def _select_variant(
        self,
        experiment: Experiment,
        assignment_key: str,
    ) -> Variant:
        """Select variant using consistent hashing."""
        # Hash the key for consistent assignment
        hash_value = int(
            hashlib.md5(
                f"{experiment.id}:{assignment_key}".encode()
            ).hexdigest(),
            16,
        )
        bucket = hash_value % 10000  # 0-9999
        
        # Map to variant based on weights
        cumulative = 0
        for variant in experiment.variants:
            cumulative += variant.weight * 100  # weight is 0-100, bucket is 0-10000
            if bucket < cumulative:
                return variant
        
        # Fallback to control
        return experiment.get_control() or experiment.variants[0]
    
    def _save_assignment(self, assignment: ExperimentAssignment) -> None:
        """Save an assignment to database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO assignments
                (id, experiment_id, variant_name, request_id, user_id, 
                 session_id, assigned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(assignment.id),
                    str(assignment.experiment_id),
                    assignment.variant_name,
                    assignment.request_id,
                    assignment.user_id,
                    assignment.session_id,
                    assignment.assigned_at.isoformat(),
                ),
            )
            conn.commit()
    
    def record_result(
        self,
        request_id: str,
        quality_score: Optional[float] = None,
        latency_ms: Optional[int] = None,
        satisfaction_score: Optional[float] = None,
        error_occurred: bool = False,
        token_count: Optional[int] = None,
    ) -> bool:
        """Record the result of an assigned request."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE assignments 
                SET quality_score = COALESCE(?, quality_score),
                    latency_ms = COALESCE(?, latency_ms),
                    satisfaction_score = COALESCE(?, satisfaction_score),
                    error_occurred = ?,
                    token_count = COALESCE(?, token_count)
                WHERE request_id = ?
                """,
                (
                    quality_score,
                    latency_ms,
                    satisfaction_score,
                    1 if error_occurred else 0,
                    token_count,
                    request_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0
    
    # ==================== Analysis ====================
    
    def get_results(self, experiment_id: UUID) -> ExperimentResult:
        """Get complete results for an experiment."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        # Get variant metrics
        variants_metrics = []
        for variant in experiment.variants:
            metrics = self._calculate_variant_metrics(experiment_id, variant.name)
            variants_metrics.append(metrics)
        
        total_samples = sum(m.sample_count for m in variants_metrics)
        
        # Calculate duration
        duration_hours = 0.0
        if experiment.started_at:
            end = experiment.ended_at or datetime.now(timezone.utc)
            duration_hours = (end - experiment.started_at).total_seconds() / 3600
        
        # Statistical comparisons
        quality_comparison = self._compare_metrics(
            variants_metrics, "quality_scores", experiment.config.confidence_level
        )
        latency_comparison = self._compare_metrics(
            variants_metrics, "latency", experiment.config.confidence_level
        )
        
        # Determine winner
        recommended_variant = None
        if quality_comparison and quality_comparison.is_significant:
            recommended_variant = quality_comparison.winner
        
        summary = self._generate_summary(
            experiment, variants_metrics, quality_comparison
        )
        
        return ExperimentResult(
            experiment_id=experiment.id,
            experiment_name=experiment.name,
            status=experiment.status,
            started_at=experiment.started_at or experiment.created_at,
            ended_at=experiment.ended_at,
            duration_hours=duration_hours,
            total_samples=total_samples,
            variants_metrics=variants_metrics,
            quality_comparison=quality_comparison,
            latency_comparison=latency_comparison,
            recommended_variant=recommended_variant,
            summary=summary,
        )
    
    def _calculate_variant_metrics(
        self,
        experiment_id: UUID,
        variant_name: str,
    ) -> VariantMetrics:
        """Calculate aggregated metrics for a variant."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT quality_score, latency_ms, satisfaction_score,
                       error_occurred, token_count
                FROM assignments
                WHERE experiment_id = ? AND variant_name = ?
                """,
                (str(experiment_id), variant_name),
            ).fetchall()
        
        metrics = VariantMetrics(variant_name=variant_name)
        metrics.sample_count = len(rows)
        
        if not rows:
            return metrics
        
        # Quality scores
        quality_scores = [r["quality_score"] for r in rows if r["quality_score"] is not None]
        if quality_scores:
            metrics.quality_scores = quality_scores
            metrics.avg_quality_score = sum(quality_scores) / len(quality_scores)
        
        # Latency
        latencies = [r["latency_ms"] for r in rows if r["latency_ms"] is not None]
        if latencies:
            sorted_lat = sorted(latencies)
            metrics.avg_latency_ms = sum(latencies) / len(latencies)
            metrics.p50_latency_ms = sorted_lat[len(sorted_lat) // 2]
            metrics.p95_latency_ms = sorted_lat[int(len(sorted_lat) * 0.95)]
            metrics.p99_latency_ms = sorted_lat[int(len(sorted_lat) * 0.99)]
        
        # Satisfaction
        satisfaction = [r["satisfaction_score"] for r in rows if r["satisfaction_score"] is not None]
        if satisfaction:
            metrics.avg_satisfaction = sum(satisfaction) / len(satisfaction)
            metrics.positive_feedback_count = sum(1 for s in satisfaction if s >= 0.7)
            metrics.negative_feedback_count = sum(1 for s in satisfaction if s < 0.4)
        
        # Errors
        metrics.error_count = sum(1 for r in rows if r["error_occurred"])
        metrics.error_rate = metrics.error_count / len(rows) if rows else 0
        
        # Tokens
        tokens = [r["token_count"] for r in rows if r["token_count"] is not None]
        if tokens:
            metrics.total_tokens = sum(tokens)
        
        return metrics
    
    def _compare_metrics(
        self,
        variants_metrics: List[VariantMetrics],
        metric_type: str,
        confidence_level: float,
    ) -> Optional[StatisticalResult]:
        """Perform statistical comparison between variants."""
        if len(variants_metrics) < 2:
            return None
        
        control = None
        treatment = None
        
        for m in variants_metrics:
            if metric_type == "quality_scores" and m.quality_scores:
                if control is None:
                    control = (m.variant_name, m.quality_scores)
                else:
                    treatment = (m.variant_name, m.quality_scores)
                    break
        
        if not control or not treatment:
            return None
        
        control_name, control_data = control
        treatment_name, treatment_data = treatment
        
        # Simple t-test approximation
        if len(control_data) < 5 or len(treatment_data) < 5:
            return StatisticalResult(
                is_significant=False,
                confidence_level=confidence_level,
                p_value=1.0,
                effect_size=0.0,
                recommendation="Insufficient data for statistical analysis",
            )
        
        control_mean = sum(control_data) / len(control_data)
        treatment_mean = sum(treatment_data) / len(treatment_data)
        
        control_std = statistics.stdev(control_data) if len(control_data) > 1 else 0
        treatment_std = statistics.stdev(treatment_data) if len(treatment_data) > 1 else 0
        
        # Pooled standard deviation
        pooled_std = ((control_std ** 2 + treatment_std ** 2) / 2) ** 0.5
        
        # Effect size (Cohen's d)
        effect_size = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0
        
        # Simple significance check
        improvement = (treatment_mean - control_mean) / control_mean if control_mean > 0 else 0
        is_significant = abs(effect_size) > 0.2 and len(control_data) >= 30
        
        # Determine winner
        winner = None
        if is_significant:
            winner = treatment_name if effect_size > 0 else control_name
        
        # Generate recommendation
        if is_significant:
            if effect_size > 0:
                rec = f"Treatment '{treatment_name}' shows significant improvement"
            else:
                rec = f"Control '{control_name}' performs better"
        else:
            rec = "No significant difference detected"
        
        return StatisticalResult(
            is_significant=is_significant,
            confidence_level=confidence_level,
            p_value=0.05 if is_significant else 0.5,  # Simplified
            effect_size=effect_size,
            winner=winner,
            improvement_percent=improvement * 100,
            recommendation=rec,
        )
    
    def _generate_summary(
        self,
        experiment: Experiment,
        variants_metrics: List[VariantMetrics],
        quality_comparison: Optional[StatisticalResult],
    ) -> str:
        """Generate a human-readable summary."""
        lines = [f"Experiment '{experiment.name}' Summary:"]
        
        total = sum(m.sample_count for m in variants_metrics)
        lines.append(f"- Total samples: {total}")
        
        for m in variants_metrics:
            lines.append(f"- {m.variant_name}: {m.sample_count} samples, avg quality: {m.avg_quality_score:.3f}")
        
        if quality_comparison:
            lines.append(f"- Statistical significance: {'Yes' if quality_comparison.is_significant else 'No'}")
            if quality_comparison.winner:
                lines.append(f"- Recommended: {quality_comparison.winner}")
        
        return "\n".join(lines)
    
    def get_active_experiments(self) -> List[Experiment]:
        """Get all currently running experiments."""
        return self.list_experiments(status=ExperimentStatus.RUNNING)


def get_experiment_manager() -> ExperimentManager:
    """Get the singleton experiment manager."""
    return ExperimentManager()
