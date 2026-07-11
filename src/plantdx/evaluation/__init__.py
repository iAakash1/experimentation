"""Evaluation package (Milestone 6): metrics, zero-shot, comparison."""

from __future__ import annotations

from plantdx.evaluation.compare import ComparisonReporter
from plantdx.evaluation.metrics import caption_metrics, classification_metrics
from plantdx.evaluation.zero_shot import ZeroShotEvaluator

__all__ = [
    "ZeroShotEvaluator",
    "ComparisonReporter",
    "classification_metrics",
    "caption_metrics",
]
