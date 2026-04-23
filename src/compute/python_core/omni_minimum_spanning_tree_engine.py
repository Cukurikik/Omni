"""OmniMinimumSpanningTreeEngine — Kruskal's MST with Union-Find.

Implements Kruskal's algorithm for minimum spanning tree computation
using edge sorting + DSU for O(E log E) performance.
"""
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMinimumSpanningTreeEngine:
    """Production engine for Kruskal's Minimum Spanning Tree."""

    ENGINE_VERSION = "1.0.0"

    def _find(self, parent, x):
        if parent[x] != x:
            parent[x] = self._find(parent, parent[x])
        return parent[x]

    def _union(self, parent, rank, x, y):
        rx, ry = self._find(parent, x), self._find(parent, y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return True

    def kruskal(self, nodes: List[str], edges: List[Tuple[str, str, float]]) -> Result:
        """
        Compute MST using Kruskal's algorithm.

        Args:
            nodes: List of node identifiers.
            edges: List of (u, v, weight) tuples.

        Returns:
            Result with MST edges, total weight, and edge count.
        """
        try:
            if not nodes:
                return Err(ValueError("Nodes must be non-empty."))
            node_idx = {n: i for i, n in enumerate(nodes)}
            n = len(nodes)
            parent = list(range(n))
            rank = [0] * n
            sorted_edges = sorted(edges, key=lambda e: e[2])
            mst_edges = []
            total_weight = 0.0

            for u, v, w in sorted_edges:
                if u not in node_idx or v not in node_idx:
                    continue
                ui, vi = node_idx[u], node_idx[v]
                if self._union(parent, rank, ui, vi):
                    mst_edges.append({"u": u, "v": v, "weight": w})
                    total_weight += w
                    if len(mst_edges) == n - 1:
                        break

            is_spanning = len(mst_edges) == n - 1
            return Ok({"mst_edges": mst_edges, "total_weight": round(total_weight, 10),
                        "edge_count": len(mst_edges), "is_spanning": is_spanning, "nodes": n})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniMinimumSpanningTreeEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(E log E) Kruskal's with DSU"}
