"""
OMNI LlamaIndex Graph Engine
Knowledge graph triplet extraction and PageRank computation over graph nodes.
"""
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniLlamaIndexGraphEngine(OmniBaseEngine):
    def __init__(self, damping: float = 0.85, max_iter: int = 100, tol: float = 1e-6):
        super().__init__()
        self.damping = damping
        self.max_iter = max_iter
        self.tol = tol

    def process(self, triplets: List[Tuple[str, str, str]]) -> Result[Dict[str, float], str]:
        if not triplets:
            return Err("Knowledge graph triplets are empty.")
            
        try:
            adjacency = defaultdict(list)
            nodes = set()
            for src, _, dst in triplets:
                adjacency[src].append(dst)
                nodes.add(src)
                nodes.add(dst)
                
            N = len(nodes)
            pagerank = {n: 1.0 / N for n in nodes}
            
            for _ in range(self.max_iter):
                prev_pagerank = pagerank.copy()
                diff = 0.0
                
                for node in nodes:
                    rank_sum = 0.0
                    for src, destinations in adjacency.items():
                        if node in destinations:
                            rank_sum += prev_pagerank[src] / len(destinations)
                            
                    pagerank[node] = (1 - self.damping) / N + self.damping * rank_sum
                    diff += abs(pagerank[node] - prev_pagerank[node])
                    
                if diff < self.tol:
                    break
                    
            return Ok(pagerank)
        except Exception as e:
            return Err(f"Graph retrieval failed: {str(e)}")

    def diagnostics(self) -> Result[Dict[str, Any], str]:
        kg = [("A", "is", "B"), ("B", "is", "C"), ("C", "is", "A")]
        res = self.process(kg)
        if hasattr(res, 'is_ok') and res.is_ok():
            return Ok({"status": "healthy", "nodes": 3, "pagerank_ran": True})
        return Err("Diagnostics failed on LlamaIndex Graph engine.")
