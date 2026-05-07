"""Generate actionable recommendations from analysis results."""

from collections import Counter
from typing import Dict, List

from sentrux.core._graph import detect_cycles
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

    return sorted(
        set(v.file_path for v in violations),
        key=lambda fp: (priority_score[fp], -violation_count[fp]),
    )


def _equality_violations(analysis: AnalysisResult) -> List[Violation]:
    if len(analysis.files) < 2:
        return []
    sizes = [f.line_count for f in analysis.files.values()]
    complexities = [f.cyclomatic_complexity for f in analysis.files.values()]
    avg_size = sum(sizes) / len(sizes) or 1
    avg_cc = sum(complexities) / len(complexities) or 1
    violations: List[Violation] = []
    for file_path, fa in analysis.files.items():
        size_ratio = fa.line_count / avg_size
        cc_ratio = fa.cyclomatic_complexity / avg_cc if avg_cc else 0
        ratio = max(size_ratio, cc_ratio)
        if ratio < 1.5:
            continue
        priority = "critical" if ratio >= 3.0 else "high" if ratio >= 2.0 else "medium"
        violations.append(
            Violation(
                file_path=file_path,
                metric="equality",
                description=(
                    f"{fa.line_count} lines ({size_ratio:.1f}x avg {avg_size:.0f}), "
                    f"CC {fa.cyclomatic_complexity:.1f} ({cc_ratio:.1f}x avg {avg_cc:.1f})"
                ),
                actual_value=round(ratio, 2),
                threshold=1.5,
                priority=priority,
            )
        )
    return violations


def _acyclicity_violations(analysis: AnalysisResult) -> List[Violation]:
    if not analysis.dependencies:
        return []
    cycles = detect_cycles(analysis.dependencies)
    violations: List[Violation] = []
    for cycle in cycles:
        cycle_str = " -> ".join(cycle)
        violations.append(
            Violation(
                file_path=cycle[0],
                metric="acyclicity",
                description=f"Circular dependency: {cycle_str}",
                actual_value=1.0,
                threshold=0.0,
                priority="critical",
            )
        )
    return violations


def _depth_violations(analysis: AnalysisResult) -> List[Violation]:
    threshold = MetricsCalculator.DEPTH_THRESHOLD
    violations: List[Violation] = []
    for file_path, fa in analysis.files.items():
        depth = MetricsCalculator._calculate_import_depth(fa.imports)
        if depth <= threshold:
            continue
        ratio = depth / threshold
        priority = "high" if ratio >= 2.0 else "medium"
        violations.append(
            Violation(
                file_path=file_path,
                metric="depth",
                description=f"Max import depth {depth} (threshold: {threshold})",
                actual_value=float(depth),
                threshold=float(threshold),
                priority=priority,
            )
        )
    return violations


def _redundancy_violations(analysis: AnalysisResult) -> List[Violation]:
    name_to_files: Dict[str, List[str]] = {}
    for file_path, fa in analysis.files.items():
        for name in fa.functions + fa.classes:
            name_to_files.setdefault(name, []).append(file_path)
    violations: List[Violation] = []
    for name, files in name_to_files.items():
        if len(files) < 2:
            continue
        violations.append(
            Violation(
                file_path=files[0],
                metric="redundancy",
                description=f"'{name}' defined in {len(files)} files: {', '.join(files)}",
                actual_value=float(len(files)),
                threshold=1.0,
                priority="low",
            )
        )
    return violations


class RecommendationEngine:
    @staticmethod
    def generate(analysis: AnalysisResult) -> DetailedReport:
        violations: List[Violation] = []
        violations += _acyclicity_violations(analysis)
        violations += _equality_violations(analysis)
        violations += _depth_violations(analysis)
        violations += _redundancy_violations(analysis)

        cycles = detect_cycles(analysis.dependencies)
        top_offenders = _rank_offenders(violations)[:3]

        return DetailedReport(
            violations=violations,
            cycles=cycles,
            top_offenders=top_offenders,
        )
