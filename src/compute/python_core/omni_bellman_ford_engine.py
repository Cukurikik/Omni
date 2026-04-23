"""OmniBellmanFordEngine — Production-grade Bellman-Ford shortest paths.

Handles negative edge weights and detects negative cycles.
O(V*E) time complexity, suitable where Dijkstra cannot be used.
"""
import math
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniBellmanFordEngine:
    """Production engine for Bellman-Ford shortest path with negative cycle detection."""

    ENGINE_VERSION = "1.0.0"

    def compute(self, nodes: List[str], edges: List[Tuple[str, str, float]], source: str) -> Result:
        """Perform compute computation.

            Args:
                    nodes: List[str]
                    edges: List[Tuple[str
                    str
                    float]]
                    source: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if source not in nodes:
                return Err(ValueError(f"Source '{source}' not in nodes."))
            dist = {n: math.inf for n in nodes}
            dist[source] = 0.0
            pred = {n: None for n in nodes}

            for _ in range(len(nodes) - 1):
                for u, v, w in edges:
                    if dist[u] + w < dist[v]:
                        dist[v] = dist[u] + w
                        pred[v] = u

            # Negative cycle detection
            for u, v, w in edges:
                if dist[u] + w < dist[v]:
                    return Err(ValueError("Negative weight cycle detected."))

            return Ok({"distances": {k: round(v, 10) if v != math.inf else None for k, v in dist.items()},
                        "predecessors": pred, "source": source, "has_negative_cycle": False})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniBellmanFordEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(V*E) with negative cycle detection"}
