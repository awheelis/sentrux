"""MCP tool implementations."""

from pathlib import Path
from typing import Any, Dict, Optional

from sentrux.core.analyzer import ProjectAnalyzer
from sentrux.core.rules import RulesEngine
from sentrux.models.analysis import AnalysisResult
from sentrux.utils.config import ConfigLoader


class MCPTools:
    """Implementations of MCP tools."""

    def scan(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Scan a directory and return analysis."""
        try:
            project_path = Path(path or ".")

            analyzer = ProjectAnalyzer(project_path)
            analysis = analyzer.analyze()

            return {
                "status": "ok",
                "result": analysis.to_dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def health(self, analysis: Optional[AnalysisResult] = None) -> Dict[str, Any]:
        """Get current health/quality metrics."""
        if analysis is None:
            return {
                "status": "ok",
                "result": {
                    "health": None,
                    "message": "No analysis data available",
                },
            }

        if analysis.quality_score is None:
            return {
                "status": "ok",
                "result": {
                    "health": None,
                    "message": "No quality score available",
                },
            }

        return {
            "status": "ok",
            "result": {
                "health": analysis.quality_score.to_dict(),
                "file_count": len(analysis.files),
            },
        }

    def check_rules(
        self,
        workspace: Optional[Path] = None,
        analysis: Optional[AnalysisResult] = None,
    ) -> Dict[str, Any]:
        """Check if rules are satisfied."""
        try:
            if workspace is None:
                workspace = Path(".")

            if analysis is None:
                analyzer = ProjectAnalyzer(workspace)
                analysis = analyzer.analyze()

            rules = ConfigLoader.load_rules(workspace)
            engine = RulesEngine(rules)
            violations = engine.check_violations(analysis)

            return {
                "status": "ok",
                "result": {
                    "violations": violations,
                    "passed": len(violations) == 0,
                    "violation_count": len(violations),
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def evolution(self, workspace: Optional[Path] = None) -> Dict[str, Any]:
        """Get quality evolution data."""
        try:
            if workspace is None:
                workspace = Path(".")

            current = ConfigLoader.load_baseline(workspace)
            analyzer = ProjectAnalyzer(workspace)
            analysis = analyzer.analyze()

            if analysis.quality_score is None:
                return {
                    "status": "ok",
                    "result": {
                        "current": None,
                        "baseline": current,
                    },
                }

            return {
                "status": "ok",
                "result": {
                    "current": analysis.quality_score.to_dict(),
                    "baseline": current,
                    "trend": (
                        "improving"
                        if current
                        and analysis.quality_score.overall_score > current.get("overall_score", 0)
                        else "declining" if current else "unknown"
                    ),
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def test_gaps(self, workspace: Optional[Path] = None) -> Dict[str, Any]:
        """Identify test coverage gaps."""
        try:
            if workspace is None:
                workspace = Path(".")

            # Find Python files without corresponding test files
            gaps = []
            from sentrux.core.parser import ProjectParser

            files = ProjectParser.parse_project(workspace)

            for file_path in files.keys():
                # Look for corresponding test file
                test_file = file_path.replace(".py", "_test.py")
                if test_file not in files:
                    gaps.append(file_path)

            return {
                "status": "ok",
                "result": {
                    "gaps": gaps,
                    "coverage_percent": (
                        ((len(files) - len(gaps)) / len(files) * 100) if files else 0
                    ),
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
