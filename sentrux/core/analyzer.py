"""Main analyzer for project code quality."""

from pathlib import Path
from typing import Dict, List, Union

from sentrux.core.metrics import MetricsCalculator
from sentrux.core.parser import ProjectParser
from sentrux.core.recommendations import RecommendationEngine
from sentrux.models.analysis import AnalysisResult


class ProjectAnalyzer:
    """Analyze a project and calculate quality metrics."""

    def __init__(self, project_path: Union[Path, str]):
        self.project_path = Path(project_path)

    def analyze(self) -> AnalysisResult:
        """Analyze the project and return results."""
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {self.project_path}")

        # Parse all files
        files = ProjectParser.parse_project(self.project_path)

        # Build dependency graph
        dependencies = self._build_dependency_graph(files)

        # Create analysis result
        analysis = AnalysisResult(
            project_path=str(self.project_path),
            files=files,
            dependencies=dependencies,
        )

        # Calculate quality score
        analysis.quality_score = MetricsCalculator.calculate_quality_score(analysis)

        # Generate actionable violation details
        analysis.detailed_report = RecommendationEngine.generate(analysis)

        return analysis

    @staticmethod
    def _build_dependency_graph(files: Dict[str, object]) -> Dict[str, List[str]]:
        """Build a dependency graph from file imports."""
        graph = {}

        for file_path, file_analysis in files.items():
            module_name = file_analysis.module_name
            if not module_name:
                continue

            graph[module_name] = file_analysis.imports

        return graph
