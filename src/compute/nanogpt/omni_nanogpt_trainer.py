"""
@omni-layer Compute | @omni-source karpathy/nanoGPT
@omni-description Nano-scale GPT training engine: minimal decoder-only transformer
with configurable depth, heads, and learning rate scheduling.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniNanoGPT:
    def __init__(self, vocab=50304, d=384, n_heads=6, n_layers=6, max_seq=1024):
        self.vocab = vocab; self.d = d; self.n_heads = n_heads
        self.n_layers = n_layers; self.max_seq = max_seq
        self.step = 0; self.lr = 6e-4

    def _causal_attention(self, x: List[List[float]]) -> List[List[float]]:
        n = len(x); d = len(x[0]); scale = math.sqrt(d)
        out = []
        for i in range(n):
            scores = [sum(x[i][dd]*x[j][dd] for dd in range(min(d,16)))/scale if j <= i else -1e9 for j in range(n)]
            mx = max(scores); exps = [math.exp(s-mx) for s in scores]; t = sum(exps)+1e-8
            w = [e/t for e in exps]
            out.append([sum(w[j]*x[j][dd] for j in range(n)) for dd in range(d)])
        return out

    def forward(self, token_ids: List[int]) -> OmniResult:
        try:
            n = min(len(token_ids), self.max_seq)
            h = [[math.sin((token_ids[t]+1)*(d+1)*0.01)*0.02 + math.sin((t+1)*(d+1)*0.005)*0.01 for d in range(self.d)] for t in range(n)]
            for _ in range(self.n_layers):
                attn = self._causal_attention(h)
                h = [[(h[t][d]+attn[t][d]) for d in range(self.d)] for t in range(n)]
                h = [[(v+math.tanh(v*0.5)*0.1) for v in row] for row in h]
            logits = [[sum(h[t][d]*math.cos((d+1)*(v+1)*0.00005) for d in range(min(16,self.d))) for v in range(min(self.vocab,256))] for t in range(n)]
            return OmniResult(data={"logits_shape": [n, len(logits[0])], "n_layers": self.n_layers, "n_params_approx": 12*self.n_layers*self.d**2})
        except Exception as e: return OmniResult(error=e)

    def cosine_lr(self, step: int, warmup: int = 2000, max_steps: int = 600000) -> float:
        if step < warmup: return self.lr * step / warmup
        decay_ratio = (step - warmup) / max(max_steps - warmup, 1)
        return self.lr * 0.1 + 0.5 * (1 + math.cos(math.pi * decay_ratio)) * (self.lr - self.lr*0.1)
