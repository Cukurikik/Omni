# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-description Mixture of Experts router: top-k expert selection with
# load balancing, capacity constraints, and auxiliary loss computation.

import math
from typing import List, Tuple

class MoERouter:
    def __init__(self, n_experts: int = 8, top_k: int = 2, d_model: int = 768, capacity_factor: float = 1.25):
        self.n_experts = n_experts
        self.top_k = top_k
        self.d_model = d_model
        self.capacity_factor = capacity_factor
        self.gate = [[math.sin(i*0.01+j*0.001)*0.1 for j in range(n_experts)] for i in range(d_model)]
        self.expert_counts = [0]*n_experts

    def route(self, tokens: List[List[float]]) -> List[List[Tuple[int, float]]]:
        n = len(tokens)
        assignments = []
        self.expert_counts = [0]*self.n_experts
        capacity = int(n * self.top_k / self.n_experts * self.capacity_factor)
        for t_idx, token in enumerate(tokens):
            scores = [sum(token[d]*self.gate[d][e] for d in range(min(len(token),self.d_model)))
                      for e in range(self.n_experts)]
            mx = max(scores)
            exps = [math.exp(s-mx) for s in scores]
            sm = sum(exps)+1e-10
            probs = [e/sm for e in exps]
            indexed = sorted(enumerate(probs), key=lambda x: -x[1])
            selected = []
            for eid, prob in indexed:
                if len(selected) >= self.top_k:
                    break
                if self.expert_counts[eid] < capacity:
                    selected.append((eid, prob))
                    self.expert_counts[eid] += 1
            if not selected:
                selected = [(indexed[0][0], indexed[0][1])]
            total = sum(p for _, p in selected)+1e-10
            selected = [(e, p/total) for e, p in selected]
            assignments.append(selected)
        return assignments

    def auxiliary_loss(self) -> float:
        total = sum(self.expert_counts)+1e-10
        fractions = [c/total for c in self.expert_counts]
        uniform = 1.0/self.n_experts
        return self.n_experts * sum(f * (f - uniform)**2 for f in fractions)

    def load_balance_stats(self) -> dict:
        total = sum(self.expert_counts)
        return {"counts": self.expert_counts[:], "total": total,
                "max_load": max(self.expert_counts), "min_load": min(self.expert_counts),
                "balance_ratio": min(self.expert_counts)/(max(self.expert_counts)+1e-10)}
