"""
@omni-layer Compute | @omni-source deep-learning-indaba/indaba-pracs-2022
@omni-description Graph Neural Network transformer engine: multi-relational message
passing with transformer-style attention over graph neighborhoods.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Tuple, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniGraphTransformer:
    def __init__(self, d=128, n_heads=4, n_layers=3):
        self.d = d; self.n_heads = n_heads; self.n_layers = n_layers

    def message_passing(self, node_feats: List[List[float]], edges: List[Tuple[int,int]]) -> OmniResult:
        try:
            n = len(node_feats); d = len(node_feats[0]) if node_feats else 0
            adj = [[] for _ in range(n)]
            for src, dst in edges:
                if src < n and dst < n: adj[dst].append(src)
            updated = []
            for i in range(n):
                if not adj[i]: updated.append(node_feats[i]); continue
                neighbors = [node_feats[j] for j in adj[i]]
                scale = math.sqrt(d)
                scores = [sum(node_feats[i][dd]*nb[dd] for dd in range(min(d,16)))/scale for nb in neighbors]
                mx = max(scores); exps = [math.exp(s-mx) for s in scores]
                t = sum(exps)+1e-8; w = [e/t for e in exps]
                msg = [sum(w[j]*neighbors[j][dd] for j in range(len(neighbors))) for dd in range(d)]
                updated.append([node_feats[i][dd]+msg[dd] for dd in range(d)])
            return OmniResult(data={"nodes": updated, "n_nodes": n, "n_edges": len(edges)})
        except Exception as e: return OmniResult(error=e)

    def forward(self, node_feats: List[List[float]], edges: List[Tuple[int,int]]) -> OmniResult:
        try:
            current = node_feats
            for _ in range(self.n_layers):
                r = self.message_passing(current, edges)
                if not r.is_ok(): return r
                current = r.data["nodes"]
                current = [[v + math.tanh(v*0.1)*0.01 for v in node] for node in current]
            pooled = [sum(current[i][d] for i in range(len(current)))/len(current) for d in range(self.d)]
            return OmniResult(data={"graph_embedding": pooled[:8], "n_layers": self.n_layers})
        except Exception as e: return OmniResult(error=e)
