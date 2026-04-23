"""OmniBipartiteMatchingEngine for Hopcroft-Karp algorithm."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniBipartiteMatchingEngine(OmniBaseEngine):
    """Production-grade Omni Bipartite Matching Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def max_matching(self, u_nodes: int, v_nodes: int, edges: List[List[int]]) -> Result[Dict[str, Any], str]:
        """
        Computes the maximum bipartite matching using Hopcroft-Karp algorithm.
        edges: list of [u, v] where 1 <= u <= u_nodes and 1 <= v <= v_nodes.
        """
        try:
            adj: Dict[int, List[int]] = {u: [] for u in range(1, u_nodes + 1)}
            for u, v in edges:
                adj[u].append(v)

            pair_u: Dict[int, int] = {u: 0 for u in range(1, u_nodes + 1)}
            pair_v: Dict[int, int] = {v: 0 for v in range(1, v_nodes + 1)}
            dist: Dict[int, float] = {}

            def bfs():
                queue = []
                for u in range(1, u_nodes + 1):
                    if pair_u[u] == 0:
                        dist[u] = 0
                        queue.append(u)
                    else:
                        dist[u] = float('inf')
                dist[0] = float('inf')

                head = 0
                while head < len(queue):
                    u = queue[head]
                    head += 1
                    if dist[u] < dist[0]:
                        for v in adj[u]:
                            if dist.get(pair_v[v], float('inf')) == float('inf'):
                                dist[pair_v[v]] = dist[u] + 1
                                queue.append(pair_v[v])
                return dist[0] != float('inf')

            def dfs(u):
                if u != 0:
                    for v in adj[u]:
                        if dist.get(pair_v[v], float('inf')) == dist[u] + 1:
                            if dfs(pair_v[v]):
                                pair_v[v] = u
                                pair_u[u] = v
                                return True
                    dist[u] = float('inf')
                    return False
                return True

            matching = 0
            while bfs():
                for u in range(1, u_nodes + 1):
                    if pair_u[u] == 0:
                        if dfs(u):
                            matching += 1

            matches = []
            for u in range(1, u_nodes + 1):
                if pair_u[u] != 0:
                    matches.append((u, pair_u[u]))

            return Result.ok({
                "max_matching": matching,
                "matches": matches
            })
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniBipartiteMatchingEngine",
            "status": "operational",
            "algorithm": "Hopcroft-Karp"
        }
