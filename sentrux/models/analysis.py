from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Metric:
    """Individual metric measurement."""
    name: str
    value: float
    description: str


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

    def to_dict(self) -> dict:
        return {
            "project_path": self.project_path,
            "quality_score": self.quality_score.to_dict() if self.quality_score else None,
            "rules_violations": self.rules_violations,
            "file_count": len(self.files),
            "dependencies": self.dependencies,
        }
