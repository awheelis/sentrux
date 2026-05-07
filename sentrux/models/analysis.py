from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Metric:
    """Individual metric measurement."""

    name: str
    value: float
    description: str


@dataclass
class Violation:
    """A specific, actionable quality violation tied to a file or cycle."""

    file_path: str
    metric: str  # "equality" | "acyclicity" | "depth" | "modularity" | "redundancy"
    description: str
    actual_value: float
    threshold: float
    priority: str  # "critical" | "high" | "medium" | "low"

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "metric": self.metric,
            "description": self.description,
            "actual_value": self.actual_value,
            "threshold": self.threshold,
            "priority": self.priority,
        }


@dataclass
class DetailedReport:
    """Structured per-file/per-cycle violations for AI agent consumption."""

    violations: List[Violation] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)
    top_offenders: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "violations": [v.to_dict() for v in self.violations],
            "cycles": self.cycles,
            "top_offenders": self.top_offenders,
        }


@dataclass
class QualityScore:
    """Overall quality score and component metrics."""

    overall_score: int  # 0-10000
    modularity: float
    acyclicity: float
    depth: float
    equality: float
    redundancy: float
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "modularity": self.modularity,
            "acyclicity": self.acyclicity,
            "depth": self.depth,
            "equality": self.equality,
            "redundancy": self.redundancy,
            "timestamp": self.timestamp,
        }


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    path: str
    module_name: str
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    cyclomatic_complexity: float = 0.0
    line_count: int = 0
    quality_score: Optional[QualityScore] = None


@dataclass
class AnalysisResult:
    """Complete analysis result for a project."""

    project_path: str
    files: Dict[str, FileAnalysis] = field(default_factory=dict)
    quality_score: Optional[QualityScore] = None
    rules_violations: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    detailed_report: Optional["DetailedReport"] = None

    def to_dict(self) -> dict:
        return {
            "project_path": self.project_path,
            "quality_score": self.quality_score.to_dict() if self.quality_score else None,
            "rules_violations": self.rules_violations,
            "file_count": len(self.files),
            "dependencies": self.dependencies,
            "detailed_report": self.detailed_report.to_dict() if self.detailed_report else None,
        }
