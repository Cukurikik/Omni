"""OmniFloydWarshallEngine — Production-grade all-pairs shortest paths.

Implements Floyd-Warshall O(V³) algorithm for solving all-pairs shortest paths
with path reconstruction and negative cycle detection.
"""
import math
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniFloydWarshallEngine:
    """Production engine for Floyd-Warshall all-pairs shortest paths."""

    ENGINE_VERSION = "1.0.0"

    def compute(self, nodes: List[str], edges: List[Tuple[str, str, float]]) -> Result:
        """Perform compute computation.

            Args:
                    nodes: List[str]
                    edges: List[Tuple[str
                    str
                    float]]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            n = len(nodes)
            idx = {node: i for i, node in enumerate(nodes)}
            dist = [[math.inf] * n for _ in range(n)]
            nxt = [[None] * n for _ in range(n)]

            for i in range(n):
                dist[i][i] = 0
            for u, v, w in edges:
                if u in idx and v in idx:
                    ui, vi = idx[u], idx[v]
                    dist[ui][vi] = w
                    nxt[ui][vi] = vi

            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        if dist[i][k] + dist[k][j] < dist[i][j]:
                            dist[i][j] = dist[i][k] + dist[k][j]
                            nxt[i][j] = nxt[i][k]

            has_neg_cycle = any(dist[i][i] < 0 for i in range(n))
            if has_neg_cycle:
                return Err(ValueError("Negative cycle detected."))

            distances = {}
            for i in range(n):
                distances[nodes[i]] = {}
                for j in range(n):
                    distances[nodes[i]][nodes[j]] = round(dist[i][j], 10) if dist[i][j] != math.inf else None

            return Ok({"distances": distances, "nodes": n, "has_negative_cycle": False})
        except Exception as e:
            return Err(e)

    def reconstruct_path(self, nodes: List[str], edges: List[Tuple[str, str, float]], source: str, target: str) -> Result:
        """Perform reconstruct path computation.

            Args:
                    nodes: List[str]
                    edges: List[Tuple[str
                    str
                    float]]
                    source: str
                    target: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            n = len(nodes)
            idx = {node: i for i, node in enumerate(nodes)}
            dist = [[math.inf] * n for _ in range(n)]
            nxt = [[None] * n for _ in range(n)]
            for i in range(n):
                dist[i][i] = 0
            for u, v, w in edges:
                if u in idx and v in idx:
                    ui, vi = idx[u], idx[v]
                    dist[ui][vi] = w
                    nxt[ui][vi] = vi
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        if dist[i][k] + dist[k][j] < dist[i][j]:
                            dist[i][j] = dist[i][k] + dist[k][j]
                            nxt[i][j] = nxt[i][k]

            si, ti = idx[source], idx[target]
            if nxt[si][ti] is None:
                return Ok({"path": None, "distance": None, "reachable": False})
            path = [si]
            while path[-1] != ti:
                path.append(nxt[path[-1]][ti])
            return Ok({"path": [nodes[i] for i in path], "distance": round(dist[si][ti], 10), "reachable": True})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniFloydWarshallEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(V³) all-pairs shortest paths"}
