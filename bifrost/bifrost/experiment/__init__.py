"""
A/B Testing Framework for Bifrost.

Provides experiment management, traffic splitting, and statistical analysis
for comparing different AI configurations and providers.
"""

from bifrost.experiment.models import (
    Experiment,
    Variant,
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    TrafficAllocation,
)
from bifrost.experiment.manager import ExperimentManager, get_experiment_manager

__all__ = [
    "Experiment",
    "Variant",
    "ExperimentConfig",
    "ExperimentResult",
    "ExperimentStatus",
    "TrafficAllocation",
    "ExperimentManager",
    "get_experiment_manager",
]
