"""Graph traversal utilities for dependency analysis."""

from typing import Dict, List


def _dfs(
    graph: Dict[str, List[str]],
    node: str,
    path: List[str],
    visited: set,
    rec_stack: set,
    cycles: List[List[str]],
) -> None:
    visited.add(node)
    rec_stack.add(node)
    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            _dfs(graph, neighbor, path + [neighbor], visited, rec_stack, cycles)
        elif neighbor in rec_stack:
            cycle_start = path.index(neighbor) if neighbor in path else 0
            cycle = path[cycle_start:] + [neighbor]
            if cycle not in cycles:
                cycles.append(cycle)
    rec_stack.discard(node)


def detect_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
    """Detect cycles in a dependency graph using DFS."""
    cycles: List[List[str]] = []
    visited: set = set()
    rec_stack: set = set()
    for node in graph:
        if node not in visited:
            _dfs(graph, node, [], visited, rec_stack, cycles)
    return cycles
