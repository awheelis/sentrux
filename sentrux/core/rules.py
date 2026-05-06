"""Rules engine for architectural governance."""

from typing import List

from sentrux.models.analysis import AnalysisResult, FileAnalysis
from sentrux.models.rules import RuleSet


class RulesEngine:
    """Check architectural rules against analysis results."""

    def __init__(self, rule_set: RuleSet):
        self.rule_set = rule_set

    def check_violations(self, analysis: AnalysisResult) -> List[str]:
        """Check for rule violations in analysis."""
        violations = []

        # Check constraints
        violations.extend(self._check_constraints(analysis))

        # Check layer boundaries
        violations.extend(self._check_boundaries(analysis))

        return violations

    def _check_constraints(self, analysis: AnalysisResult) -> List[str]:
        """Check metric constraints."""
        violations = []

        # Check max cycles constraint
        max_cycles = self.rule_set.get_constraint("max_cycles")
        if max_cycles and hasattr(analysis, "cycles"):
            cycles_count = len(getattr(analysis, "cycles", []))
            if cycles_count > max_cycles.max_value:
                violations.append(
                    f"Cycle count {cycles_count} exceeds max {max_cycles.max_value}"
                )

        # Check max cyclomatic complexity
        max_cc = self.rule_set.get_constraint("max_cc")
        if max_cc:
            for file_path, file_analysis in analysis.files.items():
                if file_analysis.cyclomatic_complexity > max_cc.max_value:
                    violations.append(
                        f"{file_path}: Cyclomatic complexity "
                        f"{file_analysis.cyclomatic_complexity:.1f} exceeds max {max_cc.max_value}"
                    )

        # Check max function length
        max_fn_lines = self.rule_set.get_constraint("max_fn_lines")
        if max_fn_lines:
            for file_path, file_analysis in analysis.files.items():
                # Rough estimate: line_count / num_functions
                if file_analysis.functions:
                    avg_fn_length = file_analysis.line_count / len(file_analysis.functions)
                    if avg_fn_length > max_fn_lines.max_value:
                        violations.append(
                            f"{file_path}: Average function length "
                            f"{avg_fn_length:.1f} exceeds max {max_fn_lines.max_value}"
                        )

        return violations

    def _check_boundaries(self, analysis: AnalysisResult) -> List[str]:
        """Check layer boundary rules."""
        violations = []

        # Map files to layers
        file_to_layer = self._map_files_to_layers(analysis)

        # Check each dependency against boundary rules
        for from_file, from_analysis in analysis.files.items():
            from_layer = file_to_layer.get(from_file)
            if not from_layer:
                continue

            for import_name in from_analysis.imports:
                # Find which layer the import belongs to
                to_layer = None
                for to_file, to_analysis in analysis.files.items():
                    if to_analysis.module_name == import_name:
                        to_layer = file_to_layer.get(to_file)
                        break

                if to_layer and not self.rule_set.is_dependency_allowed(
                    from_layer, to_layer
                ):
                    violations.append(
                        f"Boundary violation: {from_file} (layer {from_layer}) "
                        f"cannot import from {import_name} (layer {to_layer})"
                    )

        return violations

    def _map_files_to_layers(self, analysis: AnalysisResult) -> dict:
        """Map files to their layers based on patterns."""
        file_to_layer = {}

        for file_path in analysis.files.keys():
            for layer_name, layer_def in self.rule_set.layers.items():
                for pattern in layer_def.patterns:
                    if pattern in file_path or file_path.startswith(pattern):
                        file_to_layer[file_path] = layer_name
                        break

        return file_to_layer
