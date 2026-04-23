"""OmniDijkstraShortestPathEngine — Production-grade Dijkstra's shortest path.

Implements Dijkstra's algorithm using a min-heap priority queue for O((V+E)logV)
shortest path computation on weighted directed/undirected graphs represented
as adjacency lists.
"""
import heapq
import math
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniDijkstraShortestPathEngine:
    """Production engine for single-source shortest path via Dijkstra."""

    ENGINE_VERSION = "1.0.0"

    def compute_shortest_paths(self, graph: Dict[str, Dict[str, float]], source: str) -> Result:
        """
        Compute shortest paths from source to all reachable nodes.

        Args:
            graph: Adjacency list {node: {neighbor: weight, ...}, ...}.
            source: Starting node.

        Returns:
            Result with distances and predecessor map.
        """
        try:
            if not graph:
                return Err(ValueError("Graph must be non-empty."))
            if source not in graph:
                return Err(ValueError(f"Source '{source}' not in graph."))
            for u in graph:
                for v, w in graph[u].items():
                    if w < 0:
                        return Err(ValueError(f"Negative weight {w} on edge {u}->{v}. Use Bellman-Ford."))

            dist = {node: math.inf for node in graph}
            dist[source] = 0.0
            prev = {node: None for node in graph}
            pq = [(0.0, source)]
            visited = set()

            while pq:
                d, u = heapq.heappop(pq)
                if u in visited:
                    continue
                visited.add(u)
                for v, w in graph.get(u, {}).items():
                    nd = d + w
                    if nd < dist.get(v, math.inf):
                        dist[v] = nd
                        prev[v] = u
                        heapq.heappush(pq, (nd, v))

            return Ok({"distances": {k: round(v, 10) if v != math.inf else None for k, v in dist.items()},
                        "predecessors": prev, "source": source, "nodes_visited": len(visited)})
        except Exception as e:
            return Err(e)

    def reconstruct_path(self, predecessors: Dict[str, Optional[str]], target: str) -> Result:
        """Reconstruct shortest path from predecessor map."""
        try:
            path = []
            cur = target
            while cur is not None:
                path.append(cur)
                cur = predecessors.get(cur)
            path.reverse()
            if not path or path[0] == target and predecessors.get(target) is None and len(path) > 1:
                return Err(ValueError(f"No path to '{target}'."))
            return Ok({"path": path, "hops": len(path) - 1})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniDijkstraShortestPathEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O((V+E) log V) min-heap Dijkstra"}
