"""
@omni-layer Compute | @omni-source IDSIA/modern-srwm  
@omni-description Self-Referential Weight Matrix: neural net that learns to modify itself.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniSelfReferentialWeightMatrix:
    def __init__(self, d=64, n_heads=4):
        self.d = d; self.n_heads = n_heads
        self.W = [[math.sin((i+1)*(j+1)*0.01)*0.02 for j in range(d)] for i in range(d)]

    def _matmul_vec(self, M, v):
        return [sum(M[i][j]*v[j] for j in range(min(len(v),len(M[i])))) for i in range(len(M))]

    def forward(self, x: List[float]) -> OmniResult:
        try:
            h = self._matmul_vec(self.W, x)
            h = [math.tanh(v) for v in h]
            return OmniResult(data={"output": h[:8], "d": self.d})
        except Exception as e:
            return OmniResult(error=Exception(str(e)))

    def self_update(self, x: List[float], lr: float = 0.01) -> OmniResult:
        try:
            h = self._matmul_vec(self.W, x)
            delta = [[lr * h[i] * x[j] for j in range(self.d)] for i in range(self.d)]
            for i in range(self.d):
                for j in range(self.d):
                    self.W[i][j] += delta[i][j]
            norm = math.sqrt(sum(self.W[i][j]**2 for i in range(self.d) for j in range(self.d)))
            return OmniResult(data={"weight_norm": norm, "lr": lr})
        except Exception as e:
            return OmniResult(error=Exception(str(e)))
