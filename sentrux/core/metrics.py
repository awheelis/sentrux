"""Metrics calculation for code quality analysis."""

from typing import Dict, List

from sentrux.models.analysis import AnalysisResult, QualityScore


class MetricsCalculator:
    """Calculate quality metrics for code."""

    # Metric thresholds for normalization
    MODULARITY_THRESHOLD = 0.8
    ACYCLICITY_THRESHOLD = 0.9
    DEPTH_THRESHOLD = 5
    EQUALITY_THRESHOLD = 0.7
    REDUNDANCY_THRESHOLD = 0.95

    @staticmethod
    def calculate_quality_score(analysis: AnalysisResult) -> QualityScore:
        """Calculate overall quality score from analysis."""
        modularity = MetricsCalculator._calculate_modularity(analysis)
        acyclicity = MetricsCalculator._calculate_acyclicity(analysis)
        depth = MetricsCalculator._calculate_depth(analysis)
        equality = MetricsCalculator._calculate_equality(analysis)
        redundancy = MetricsCalculator._calculate_redundancy(analysis)

        # Normalize each metric to 0-1 and weight them
        weights = {
            "modularity": 0.25,
            "acyclicity": 0.25,
            "depth": 0.2,
            "equality": 0.15,
            "redundancy": 0.15,
        }

        overall = (
            modularity * weights["modularity"]
            + acyclicity * weights["acyclicity"]
            + depth * weights["depth"]
            + equality * weights["equality"]
            + redundancy * weights["redundancy"]
        )

        # Scale to 0-10000
        overall_score = int(overall * 10000)

        return QualityScore(
            overall_score=overall_score,
            modularity=modularity,
            acyclicity=acyclicity,
            depth=depth,
            equality=equality,
            redundancy=redundancy,
        )

    @staticmethod
    def _calculate_modularity(analysis: AnalysisResult) -> float:
        """Calculate modularity metric (internal vs external dependencies)."""
        if not analysis.files:
            return 1.0

        total_dependencies = 0
        internal_dependencies = 0

        for file_analysis in analysis.files.values():
            for imp in file_analysis.imports:
                total_dependencies += 1
                # Check if import is from project
                if MetricsCalculator._is_internal_import(imp, analysis):
                    internal_dependencies += 1

        if total_dependencies == 0:
            return 1.0

        # Higher internal coupling = lower modularity
        modularity = 1.0 - (internal_dependencies / total_dependencies)
        return min(1.0, max(0.0, modularity))

    @staticmethod
    def _calculate_acyclicity(analysis: AnalysisResult) -> float:
        """Calculate acyclicity metric (presence of circular dependencies)."""
        if not analysis.dependencies:
            return 1.0

        # Simple cycle detection in dependency graph
        cycles = MetricsCalculator._detect_cycles(analysis.dependencies)
        cycle_count = len(cycles)

        # More cycles = lower acyclicity
        if cycle_count == 0:
            return 1.0

        # Penalty based on number of cycles
        acyclicity = 1.0 - min(1.0, cycle_count * 0.2)
        return max(0.0, acyclicity)

    @staticmethod
    def _calculate_depth(analysis: AnalysisResult) -> float:
        """Calculate depth metric (import nesting depth)."""
        if not analysis.files:
            return 1.0

        max_depth = 1
        for file_analysis in analysis.files.values():
            depth = MetricsCalculator._calculate_import_depth(file_analysis.imports)
            max_depth = max(max_depth, depth)

        # Normalize: deeper = lower score
        depth_score = max(0.0, 1.0 - (max_depth / MetricsCalculator.DEPTH_THRESHOLD))
        return min(1.0, depth_score)

    @staticmethod
    def _calculate_equality(analysis: AnalysisResult) -> float:
        """Calculate equality metric (uniformity of file sizes/complexity)."""
        if len(analysis.files) < 2:
            return 1.0

        sizes = [f.line_count for f in analysis.files.values()]
        complexities = [f.cyclomatic_complexity for f in analysis.files.values()]

        avg_size = sum(sizes) / len(sizes)
        avg_complexity = sum(complexities) / len(complexities)

        if avg_size == 0 or avg_complexity == 0:
            return 1.0

        # Calculate variance
        size_variance = sum((s - avg_size) ** 2 for s in sizes) / len(sizes)
        complexity_variance = (
            sum((c - avg_complexity) ** 2 for c in complexities) / len(complexities)
        )

        # Normalize to 0-1 (lower variance = higher equality)
        size_cv = (size_variance ** 0.5) / (avg_size or 1)
        complexity_cv = (complexity_variance ** 0.5) / (avg_complexity or 1)

        equality = 1.0 - min(1.0, (size_cv + complexity_cv) / 4)
        return max(0.0, equality)

    @staticmethod
    def _calculate_redundancy(analysis: AnalysisResult) -> float:
        """Calculate redundancy metric (code duplication detection)."""
        if not analysis.files:
            return 1.0

        # Simple duplicate detection based on function/class names
        all_functions = []
        all_classes = []

        for file_analysis in analysis.files.values():
            all_functions.extend(file_analysis.functions)
            all_classes.extend(file_analysis.classes)

        total_items = len(all_functions) + len(all_classes)
        if total_items == 0:
            return 1.0

        unique_items = len(set(all_functions)) + len(set(all_classes))

        # Higher uniqueness = higher redundancy score
        if total_items == 0:
            return 1.0

        redundancy = unique_items / total_items
        return min(1.0, max(0.0, redundancy))

    @staticmethod
    def _is_internal_import(module: str, analysis: AnalysisResult) -> bool:
        """Check if module is internal to the project."""
        # Simple heuristic: if any file has this module name
        project_modules = set()
        for file_path in analysis.files.keys():
            parts = file_path.replace("\\", "/").split("/")
            project_modules.add(parts[0])

        return module in project_modules

    @staticmethod
    def _detect_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect cycles in dependency graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path + [neighbor])
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            rec_stack.discard(node)

        for node in graph:
            if node not in visited:
                dfs(node, [node])

        return cycles

    @staticmethod
    def _calculate_import_depth(imports: List[str]) -> int:
        """Calculate maximum import nesting depth."""
        if not imports:
            return 0

        max_depth = 0
        for imp in imports:
            depth = len(imp.split("."))
            max_depth = max(max_depth, depth)

        return max_depth
