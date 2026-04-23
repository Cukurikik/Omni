"""OmniMaxFlowEngine — Production-grade max flow (Edmonds-Karp / BFS Ford-Fulkerson).

Implements Edmonds-Karp algorithm for maximum flow computation in directed graphs.
O(V * E²) time complexity using BFS for shortest augmenting paths.
"""
from collections import deque
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMaxFlowEngine:
    """Production engine for maximum flow using Edmonds-Karp algorithm."""

    ENGINE_VERSION = "1.0.0"

    def compute(self, nodes: List[str], edges: List[Tuple[str, str, float]],
                source: str, sink: str) -> Result:
        """Perform maximum flow computation using Edmonds-Karp algorithm.

        Args:
            nodes: List of node identifiers in the graph.
            edges: List of (source, target, capacity) edge tuples.
            source: The source node identifier.
            sink: The sink node identifier.

        Returns:
            Result: Monadic result wrapping the max flow value or error.
        """
        try:
            if source not in nodes or sink not in nodes:
                return Err(ValueError("Source and sink must be valid nodes."))
            idx = {n: i for i, n in enumerate(nodes)}
            n = len(nodes)
            cap = [[0.0] * n for _ in range(n)]
            for u, v, c in edges:
                if u in idx and v in idx:
                    cap[idx[u]][idx[v]] += c

            flow = [[0.0] * n for _ in range(n)]
            total_flow = 0.0
            s, t = idx[source], idx[sink]

            while True:
                parent = [-1] * n
                parent[s] = s
                queue = deque([s])
                while queue and parent[t] == -1:
                    u = queue.popleft()
                    for v in range(n):
                        if parent[v] == -1 and cap[u][v] - flow[u][v] > 1e-9:
                            parent[v] = u
                            queue.append(v)
                if parent[t] == -1:
                    break
                # Find bottleneck
                bottleneck = float('inf')
                v = t
                while v != s:
                    u = parent[v]
                    bottleneck = min(bottleneck, cap[u][v] - flow[u][v])
                    v = u
                # Update flow
                v = t
                while v != s:
                    u = parent[v]
                    flow[u][v] += bottleneck
                    flow[v][u] -= bottleneck
                    v = u
                total_flow += bottleneck

            return Ok({"max_flow": round(total_flow, 10), "source": source, "sink": sink, "nodes": n})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniMaxFlowEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(V * E²) Edmonds-Karp"}
