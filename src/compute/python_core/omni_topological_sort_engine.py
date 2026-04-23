"""OmniTopologicalSortEngine — Production-grade topological sorting.

Implements Kahn's algorithm (BFS-based) for topological sorting of DAGs,
with cycle detection and dependency resolution.
"""
from typing import Any, Dict, List, Set
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniTopologicalSortEngine:
    """Production engine for topological sorting of directed acyclic graphs."""

    ENGINE_VERSION = "1.0.0"

    def sort(self, graph: Dict[str, List[str]]) -> Result:
        """
        Perform topological sort using Kahn's algorithm.

        Args:
            graph: Adjacency list {node: [dependency_targets]}.

        Returns:
            Result with topological order or cycle detection.
        """
        try:
            if not graph:
                return Err(ValueError("Graph must be non-empty."))

            all_nodes: Set[str] = set(graph.keys())
            for targets in graph.values():
                for t in targets:
                    all_nodes.add(t)

            in_degree = {n: 0 for n in all_nodes}
            for node, targets in graph.items():
                for t in targets:
                    in_degree[t] = in_degree.get(t, 0) + 1

            queue = sorted([n for n in all_nodes if in_degree[n] == 0])
            result = []

            while queue:
                node = queue.pop(0)
                result.append(node)
                for target in graph.get(node, []):
                    in_degree[target] -= 1
                    if in_degree[target] == 0:
                        # Insert sorted for determinism
                        idx = 0
                        while idx < len(queue) and queue[idx] < target:
                            idx += 1
                        queue.insert(idx, target)

            if len(result) != len(all_nodes):
                return Err(ValueError("Graph contains a cycle; topological sort impossible."))

            return Ok({"order": result, "total_nodes": len(result), "has_cycle": False})
        except Exception as e:
            return Err(e)

    def find_all_paths(self, graph: Dict[str, List[str]], source: str, target: str) -> Result:
        """Find all paths from source to target in a DAG."""
        try:
            if source not in graph and source != target:
                return Err(ValueError(f"Source '{source}' not in graph."))
            paths = []

            def dfs(node, path):
                if node == target:
                    paths.append(path[:])
                    return
                for neighbor in graph.get(node, []):
                    path.append(neighbor)
                    dfs(neighbor, path)
                    path.pop()

            dfs(source, [source])
            return Ok({"paths": paths, "count": len(paths), "source": source, "target": target})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniTopologicalSortEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(V + E) Kahn's algorithm"}
