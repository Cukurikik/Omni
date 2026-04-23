"""OmniPageRankEngine — Production-grade PageRank computation.

Implements the iterative power method for computing PageRank scores
on directed graphs with configurable damping factor and convergence tolerance.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniPageRankEngine:
    """Production engine for PageRank computation via power iteration."""

    ENGINE_VERSION = "1.0.0"

    def compute(self, graph: Dict[str, List[str]], damping: float = 0.85,
                max_iter: int = 100, tol: float = 1e-8) -> Result:
        """
        Compute PageRank scores for all nodes in a directed graph.

        Args:
            graph: Adjacency list {node: [outgoing_neighbors]}.
            damping: Damping factor d (typically 0.85).
            max_iter: Maximum iterations.
            tol: Convergence tolerance (L1 norm of rank change).

        Returns:
            Result with PageRank scores, iterations, and convergence status.
        """
        try:
            if not graph:
                return Err(ValueError("Graph must be non-empty."))
            if not (0 < damping < 1):
                return Err(ValueError("Damping factor must be in (0, 1)."))

            nodes = set(graph.keys())
            for outlinks in graph.values():
                for v in outlinks:
                    nodes.add(v)
            nodes = sorted(nodes)
            n = len(nodes)
            node_idx = {node: i for i, node in enumerate(nodes)}

            rank = [1.0 / n] * n
            iters = 0
            converged = False

            for it in range(max_iter):
                iters = it + 1
                new_rank = [(1.0 - damping) / n] * n

                dangling_sum = 0.0
                for node in nodes:
                    i = node_idx[node]
                    outlinks = graph.get(node, [])
                    if not outlinks:
                        dangling_sum += rank[i]
                    else:
                        share = rank[i] / len(outlinks)
                        for v in outlinks:
                            j = node_idx[v]
                            new_rank[j] += damping * share

                dangling_contrib = damping * dangling_sum / n
                for i in range(n):
                    new_rank[i] += dangling_contrib

                diff = sum(abs(new_rank[i] - rank[i]) for i in range(n))
                rank = new_rank
                if diff < tol:
                    converged = True
                    break

            result = {nodes[i]: round(rank[i], 10) for i in range(n)}
            sorted_ranks = sorted(result.items(), key=lambda x: -x[1])

            return Ok({"ranks": result, "sorted_ranks": [{"node": k, "score": v} for k, v in sorted_ranks],
                        "iterations": iters, "converged": converged, "damping": damping,
                        "total_nodes": n})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniPageRankEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(V + E) per iteration power method"}
