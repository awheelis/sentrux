from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Constraint:
    """A single constraint rule."""

    name: str
    max_value: Optional[int] = None
    description: str = ""


@dataclass
class LayerDefinition:
    """Definition of a code layer."""

    name: str
    patterns: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class BoundaryRule:
    """A boundary rule between layers."""

    source_layer: str
    target_layer: str
    allowed: bool = False
    description: str = ""


@dataclass
class RuleSet:
    """Complete set of architectural rules."""

    constraints: Dict[str, Constraint] = field(default_factory=dict)
    layers: Dict[str, LayerDefinition] = field(default_factory=dict)
    layer_order: List[str] = field(default_factory=list)
    boundaries: List[BoundaryRule] = field(default_factory=list)

    def get_constraint(self, name: str) -> Optional[Constraint]:
        return self.constraints.get(name)

    def get_layer(self, name: str) -> Optional[LayerDefinition]:
        return self.layers.get(name)

    def is_dependency_allowed(self, from_layer: str, to_layer: str) -> bool:
        """Check if dependency from source to target layer is allowed."""
        for rule in self.boundaries:
            if rule.source_layer == from_layer and rule.target_layer == to_layer:
                return rule.allowed
        return True
