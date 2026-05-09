"""
@omni-layer Compute | @omni-source facebookresearch/llama
@omni-description RoPE (Rotary Position Embedding) engine: complex-number rotation
of query/key pairs for relative position encoding.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Tuple

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniRoPE:
    def __init__(self, d=64, base=10000.0, max_seq=4096):
        self.d = d; self.base = base; self.max_seq = max_seq
        self.freqs = self._precompute_freqs()

    def _precompute_freqs(self) -> List[List[Tuple[float,float]]]:
        freqs = []
        for pos in range(self.max_seq):
            pos_freqs = []
            for i in range(self.d // 2):
                theta = pos / (self.base ** (2*i / self.d))
                pos_freqs.append((math.cos(theta), math.sin(theta)))
            freqs.append(pos_freqs)
        return freqs

    def apply_rotary(self, x: List[float], position: int) -> OmniResult:
        try:
            if position >= self.max_seq: return OmniResult(error=Exception("Position OOB"))
            d = len(x); rotated = list(x)
            freqs = self.freqs[position]
            for i in range(min(d//2, len(freqs))):
                cos_t, sin_t = freqs[i]
                x0, x1 = x[2*i], x[2*i+1]
                rotated[2*i] = x0*cos_t - x1*sin_t
                rotated[2*i+1] = x0*sin_t + x1*cos_t
            return OmniResult(data={"rotated": rotated, "position": position})
        except Exception as e: return OmniResult(error=e)

    def apply_batch(self, queries: List[List[float]], keys: List[List[float]], start_pos: int = 0) -> OmniResult:
        try:
            rot_q = []; rot_k = []
            for i in range(len(queries)):
                rq = self.apply_rotary(queries[i], start_pos+i)
                rk = self.apply_rotary(keys[i], start_pos+i)
                if not rq.is_ok() or not rk.is_ok(): return OmniResult(error=Exception("Rotation failed"))
                rot_q.append(rq.data["rotated"]); rot_k.append(rk.data["rotated"])
            return OmniResult(data={"queries": rot_q, "keys": rot_k, "n_tokens": len(queries)})
        except Exception as e: return OmniResult(error=e)
