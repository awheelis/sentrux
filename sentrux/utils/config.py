"""Configuration loading from .sentrux/rules.toml."""

import sys
from pathlib import Path
from typing import Optional, Union

# Use tomllib on Python 3.11+, otherwise tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

from sentrux.models.rules import BoundaryRule, Constraint, LayerDefinition, RuleSet


class ConfigLoader:
    """Load and parse configuration from .sentrux/rules.toml."""

    DEFAULT_RULES_DIR = ".sentrux"
    DEFAULT_RULES_FILE = "rules.toml"

    @staticmethod
    def load_rules(project_path: Union[Path, str]) -> RuleSet:
        """Load rules from project directory."""
        project_path = Path(project_path)
        rules_file = project_path / ConfigLoader.DEFAULT_RULES_DIR / ConfigLoader.DEFAULT_RULES_FILE

        if not rules_file.exists():
            return RuleSet()

        if tomllib is None:
            # If no TOML library available, return empty rules
            return RuleSet()

        try:
            with open(rules_file, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            return RuleSet()

        return ConfigLoader._parse_rules(data)

    @staticmethod
    def _parse_rules(data: dict) -> RuleSet:
        """Parse TOML data into RuleSet."""
        rule_set = RuleSet()

        # Parse constraints
        constraints_data = data.get("constraints", {})
        if isinstance(constraints_data, dict):
            for name, value in constraints_data.items():
                if isinstance(value, dict):
                    # New format: {max: value, description: ...}
                    constraint = Constraint(
                        name=name,
                        max_value=value.get("max"),
                        description=value.get("description", ""),
                    )
                    rule_set.constraints[name] = constraint
                else:
                    # Old format: just the value
                    constraint = Constraint(
                        name=name,
                        max_value=value,
                        description="",
                    )
                    rule_set.constraints[name] = constraint

        # Parse layers (can be array of tables or dict)
        layers_data = data.get("layers", [])
        if isinstance(layers_data, list):
            for config in layers_data:
                if isinstance(config, dict):
                    layer = LayerDefinition(
                        name=config.get("name", ""),
                        patterns=config.get("paths", config.get("patterns", [])),
                        description=config.get("description", ""),
                    )
                    rule_set.layers[layer.name] = layer
                    rule_set.layer_order.append(layer.name)
        else:
            for name, config in layers_data.items():
                if isinstance(config, dict):
                    layer = LayerDefinition(
                        name=name,
                        patterns=config.get("patterns", []),
                        description=config.get("description", ""),
                    )
                    rule_set.layers[name] = layer

        # Parse boundaries (array of tables)
        boundaries_data = data.get("boundaries", [])
        for boundary in boundaries_data:
            if isinstance(boundary, dict):
                rule = BoundaryRule(
                    source_layer=boundary.get("from", ""),
                    target_layer=boundary.get("to", ""),
                    allowed=boundary.get("allowed", False),
                    description=boundary.get("reason", boundary.get("description", "")),
                )
                rule_set.boundaries.append(rule)

        return rule_set

    @staticmethod
    def save_baseline(project_path: Union[Path, str], baseline_data: dict) -> None:
        """Save quality baseline for comparison."""
        project_path = Path(project_path)
        rules_dir = project_path / ConfigLoader.DEFAULT_RULES_DIR
        rules_dir.mkdir(exist_ok=True)

        baseline_file = rules_dir / "baseline.toml"

        if tomllib is None:
            return

        # Simple baseline saving (not using TOML format for write due to complexity)
        try:
            with open(baseline_file, "w") as f:
                f.write("# Quality baseline\n")
                f.write("[baseline]\n")
                for key, value in baseline_data.items():
                    if isinstance(value, (int, float)):
                        f.write(f"{key} = {value}\n")
        except Exception:
            pass

    @staticmethod
    def load_baseline(project_path: Union[Path, str]) -> Optional[dict]:
        """Load saved quality baseline."""
        project_path = Path(project_path)
        baseline_file = project_path / ConfigLoader.DEFAULT_RULES_DIR / "baseline.toml"

        if not baseline_file.exists():
            return None

        if tomllib is None:
            return None

        try:
            with open(baseline_file, "rb") as f:
                data = tomllib.load(f)
            return data.get("baseline", {})
        except Exception:
            return None
