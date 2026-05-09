"""
OMNI Compute — Rotary Position Embedding (RoPE) Library
Production RoPE implementation with NTK-aware scaling.
"""
import math, logging
from dataclasses import dataclass
from typing import Tuple, Optional, List

logger = logging.getLogger("omni.rope")

@dataclass
class RoPEConfig:
    dim: int = 128; max_seq_len: int = 8192; base: float = 10000.0
    scaling_type: str = "none"  # none | linear | ntk | yarn
    scaling_factor: float = 1.0; ntk_alpha: float = 1.0
    original_max_len: int = 4096

class OmniRoPE:
    """Rotary Position Embedding with multiple scaling strategies."""
    def __init__(self, config: RoPEConfig):
        self.config = config
        self.inv_freq = self._compute_inv_freq()
        self.cos_cache: Optional[List[List[float]]] = None
        self.sin_cache: Optional[List[List[float]]] = None
        self._build_cache()
    def _compute_inv_freq(self) -> List[float]:
        dim = self.config.dim; base = self.config.base
        if self.config.scaling_type == "ntk":
            base = base * ((self.config.scaling_factor * self.config.max_seq_len / self.config.original_max_len)
                          - (self.config.scaling_factor - 1)) ** (dim / (dim - 2))
        inv_freq = []
        for i in range(0, dim, 2):
            freq = 1.0 / (base ** (i / dim))
            if self.config.scaling_type == "linear":
                freq /= self.config.scaling_factor
            inv_freq.append(freq)
        return inv_freq
    def _build_cache(self):
        seq = self.config.max_seq_len
        half_dim = len(self.inv_freq)
        self.cos_cache = [[0.0] * half_dim for _ in range(seq)]
        self.sin_cache = [[0.0] * half_dim for _ in range(seq)]
        for pos in range(seq):
            for i, freq in enumerate(self.inv_freq):
                angle = pos * freq
                self.cos_cache[pos][i] = math.cos(angle)
                self.sin_cache[pos][i] = math.sin(angle)
    def apply(self, q: List[List[float]], k: List[List[float]], positions: List[int]) -> Tuple[List[List[float]], List[List[float]]]:
        """Apply RoPE to query and key tensors."""
        rotated_q, rotated_k = [], []
        half = len(self.inv_freq)
        for idx, pos in enumerate(positions):
            cos = self.cos_cache[pos]
            sin = self.sin_cache[pos]
            rq, rk = [], []
            for i in range(half):
                rq.append(q[idx][i] * cos[i] - q[idx][i + half] * sin[i])
                rq.append(q[idx][i + half] * cos[i] + q[idx][i] * sin[i])
                rk.append(k[idx][i] * cos[i] - k[idx][i + half] * sin[i])
                rk.append(k[idx][i + half] * cos[i] + k[idx][i] * sin[i])
            rotated_q.append(rq); rotated_k.append(rk)
        return rotated_q, rotated_k
    def get_config_info(self) -> dict:
        return {"dim": self.config.dim, "max_seq_len": self.config.max_seq_len,
                "base": self.config.base, "scaling": self.config.scaling_type,
                "cache_size": len(self.cos_cache) if self.cos_cache else 0}
