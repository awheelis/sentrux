"""Generate actionable recommendations from analysis results."""

from collections import Counter
from typing import List

from sentrux.core.metrics import MetricsCalculator
from sentrux.models.analysis import AnalysisResult, DetailedReport, Violation

_PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _rank_offenders(violations: List[Violation]) -> List[str]:
    """Return file paths ranked by worst priority and most violations."""
    priority_score: Counter = Counter()
    violation_count: Counter = Counter()

    for v in violations:
        priority_score[v.file_path] += _PRIORITY_ORDER.get(v.priority, 3)
        violation_count[v.file_path] += 1

    # Lower priority_score = more critical; break ties by violation count (higher wins)
    return sorted(
        set(v.file_path for v in violations),
        key=lambda fp: (priority_score[fp], -violation_count[fp]),
    )


class RecommendationEngine:
    @staticmethod
    def generate(analysis: AnalysisResult) -> DetailedReport:
        violations: List[Violation] = []
        violations += MetricsCalculator._get_acyclicity_violations(analysis)
        violations += MetricsCalculator._get_equality_violations(analysis)
        violations += MetricsCalculator._get_depth_violations(analysis)
        violations += MetricsCalculator._get_redundancy_violations(analysis)

        cycles = MetricsCalculator._detect_cycles(analysis.dependencies)
        top_offenders = _rank_offenders(violations)[:3]

        return DetailedReport(
            violations=violations,
            cycles=cycles,
            top_offenders=top_offenders,
        )
