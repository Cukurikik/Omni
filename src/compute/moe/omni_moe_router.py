"""
@omni-layer Compute | @omni-source microsoft/DeepSpeed (MoE concepts)
@omni-description Mixture of Experts router: top-k expert selection with load
balancing and auxiliary loss for uniform expert utilization.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniMoERouter:
    def __init__(self, d=512, n_experts=8, top_k=2, capacity_factor=1.25):
        self.d = d; self.n_experts = n_experts; self.top_k = top_k
        self.capacity_factor = capacity_factor
        self.gate_weights = [[math.sin((e+1)*(j+1)*0.004)*0.05 for j in range(d)] for e in range(n_experts)]

    def route(self, token_embeddings: List[List[float]]) -> OmniResult:
        try:
            n = len(token_embeddings)
            assignments = []; load = [0]*self.n_experts
            capacity = int(math.ceil(n * self.top_k / self.n_experts * self.capacity_factor))
            for emb in token_embeddings:
                scores = [sum(self.gate_weights[e][j]*emb[j] for j in range(min(len(emb),self.d))) for e in range(self.n_experts)]
                mx = max(scores); exps = [math.exp(s-mx) for s in scores]; t = sum(exps)
                probs = [e/t for e in exps]
                top_experts = sorted(range(self.n_experts), key=lambda e: -probs[e])[:self.top_k]
                selected = []
                for e in top_experts:
                    if load[e] < capacity:
                        selected.append({"expert": e, "weight": probs[e]})
                        load[e] += 1
                assignments.append(selected)
            balance_loss = self._load_balance_loss(load, n)
            return OmniResult(data={"assignments": assignments[:5], "load": load, "balance_loss": balance_loss, "capacity": capacity, "n_tokens": n})
        except Exception as e: return OmniResult(error=e)

    def _load_balance_loss(self, load: List[int], n_tokens: int) -> float:
        ideal = n_tokens * self.top_k / self.n_experts
        return sum((l - ideal)**2 for l in load) / (self.n_experts * max(ideal**2, 1))
