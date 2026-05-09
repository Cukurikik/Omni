# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo commented-transformers + Transformers-in-Action
# @omni-description Positional encoding library: implements RoPE, ALiBi,
# learnable PE, sinusoidal PE, and relative PE for transformer architectures.

import math
from typing import List, Tuple

class SinusoidalPE:
    def __init__(self, d: int = 768, max_len: int = 8192):
        self.d, self.max_len = d, max_len
        self.pe = [[0.0]*d for _ in range(max_len)]
        for pos in range(max_len):
            for i in range(0, d, 2):
                freq = 1.0 / (10000 ** (i / d))
                self.pe[pos][i] = math.sin(pos * freq)
                if i+1 < d: self.pe[pos][i+1] = math.cos(pos * freq)
    def encode(self, seq_len: int) -> List[List[float]]:
        return self.pe[:seq_len]

class RoPE:
    def __init__(self, d: int = 768, base: float = 10000.0):
        self.d, self.base = d, base
    def apply(self, x: List[List[float]], offset: int = 0) -> List[List[float]]:
        result = [row[:] for row in x]
        for pos in range(len(x)):
            for i in range(0, min(self.d, len(x[0])), 2):
                freq = 1.0 / (self.base ** (i / self.d))
                angle = (pos + offset) * freq
                c, s = math.cos(angle), math.sin(angle)
                x0, x1 = result[pos][i], result[pos][i+1] if i+1 < len(x[0]) else 0
                result[pos][i] = x0*c - x1*s
                if i+1 < len(x[0]): result[pos][i+1] = x0*s + x1*c
        return result

class ALiBi:
    def __init__(self, n_heads: int = 12):
        self.n_heads = n_heads
        self.slopes = [2 ** (-(8 * (h+1)) / n_heads) for h in range(n_heads)]
    def bias(self, seq_len: int, head: int) -> List[List[float]]:
        m = self.slopes[head % self.n_heads]
        return [[m * (j - i) if j <= i else -1e9 for j in range(seq_len)] for i in range(seq_len)]

class LearnablePE:
    def __init__(self, d: int = 768, max_len: int = 2048):
        self.d, self.max_len = d, max_len
        self.weights = [[math.sin(pos*0.01+d*0.001)*0.02 for d in range(self.d)] for pos in range(max_len)]
    def encode(self, seq_len: int) -> List[List[float]]:
        return self.weights[:seq_len]
    def update(self, pos: int, gradient: List[float], lr: float = 0.001):
        for d in range(min(len(gradient), self.d)):
            self.weights[pos][d] -= lr * gradient[d]

class RelativePE:
    def __init__(self, max_dist: int = 128, d: int = 64):
        self.max_dist, self.d = max_dist, d
        self.embeddings = {}
        for dist in range(-max_dist, max_dist+1):
            self.embeddings[dist] = [math.sin(dist*0.1+d*0.01)*0.1 for d in range(self.d)]
    def get_bias(self, i: int, j: int) -> List[float]:
        dist = max(-self.max_dist, min(self.max_dist, j - i))
        return self.embeddings.get(dist, [0.0]*self.d)
    def attention_bias(self, seq_len: int) -> List[List[float]]:
        bias = [[0.0]*seq_len for _ in range(seq_len)]
        for i in range(seq_len):
            for j in range(seq_len):
                rel = self.get_bias(i, j)
                bias[i][j] = sum(rel[:8]) * 0.1
        return bias

class PositionalEncodingFactory:
    @staticmethod
    def create(method: str, **kwargs):
        if method == "sinusoidal": return SinusoidalPE(**kwargs)
        if method == "rope": return RoPE(**kwargs)
        if method == "alibi": return ALiBi(**kwargs)
        if method == "learnable": return LearnablePE(**kwargs)
        if method == "relative": return RelativePE(**kwargs)
        raise ValueError(f"Unknown PE method: {method}")
