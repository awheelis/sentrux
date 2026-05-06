"""Sentrux - Structural quality analysis and governance for code."""

__version__ = "0.1.0"

from sentrux.core.analyzer import ProjectAnalyzer
from sentrux.models.analysis import AnalysisResult, QualityScore

__all__ = ["ProjectAnalyzer", "AnalysisResult", "QualityScore"]
