"""
OMNI Compute — Model Merging Engine (mergekit-inspired)
SLERP, TIES, DARE model merging for ensemble creation.
"""
import logging, math
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("omni.merge")

@dataclass
class MergeConfig:
    method: str = "slerp"         # slerp | ties | dare | linear
    interpolation: float = 0.5    # 0.0 = model_a, 1.0 = model_b
    density: float = 0.5          # TIES/DARE sparsity
    normalize: bool = True

class OmniModelMerger:
    """Production model merging engine supporting multiple algorithms."""
    def __init__(self, config: MergeConfig):
        self.config = config
    def linear_merge(self, a: List[float], b: List[float], t: float) -> List[float]:
        """Linear interpolation: (1-t)*a + t*b"""
        return [(1-t)*ai + t*bi for ai, bi in zip(a, b)]
    def slerp_merge(self, a: List[float], b: List[float], t: float) -> List[float]:
        """Spherical linear interpolation for weight merging."""
        dot = sum(ai*bi for ai, bi in zip(a, b))
        norm_a = math.sqrt(sum(x*x for x in a)) or 1e-8
        norm_b = math.sqrt(sum(x*x for x in b)) or 1e-8
        dot = dot / (norm_a * norm_b)
        dot = max(-1.0, min(1.0, dot))
        omega = math.acos(dot)
        if abs(omega) < 1e-6:
            return self.linear_merge(a, b, t)
        sin_omega = math.sin(omega)
        s1 = math.sin((1-t)*omega) / sin_omega
        s2 = math.sin(t*omega) / sin_omega
        return [s1*ai + s2*bi for ai, bi in zip(a, b)]
    def ties_merge(self, models: List[List[float]], base: List[float]) -> List[float]:
        """TIES: Trim, Elect Sign, Merge."""
        n = len(models); dim = len(base)
        # Compute task vectors (delta from base)
        deltas = [[m[i] - base[i] for i in range(dim)] for m in models]
        result = list(base)
        for i in range(dim):
            values = [d[i] for d in deltas]
            # Trim: keep top-density magnitudes
            abs_vals = sorted(enumerate(values), key=lambda x: abs(x[1]), reverse=True)
            keep = max(1, int(len(abs_vals) * self.config.density))
            trimmed = [0.0] * n
            for idx, (orig_idx, v) in enumerate(abs_vals[:keep]):
                trimmed[orig_idx] = v
            # Elect sign: majority vote
            pos = sum(1 for v in trimmed if v > 0)
            neg = sum(1 for v in trimmed if v < 0)
            elected_sign = 1 if pos >= neg else -1
            # Merge: average same-sign values
            same_sign = [v for v in trimmed if v != 0 and (v > 0) == (elected_sign > 0)]
            if same_sign:
                result[i] = base[i] + sum(same_sign) / len(same_sign)
        return result
    def dare_merge(self, a: List[float], b: List[float], base: List[float]) -> List[float]:
        """DARE: Drop And REscale merging."""
        import random
        dim = len(base)
        delta_a = [a[i] - base[i] for i in range(dim)]
        delta_b = [b[i] - base[i] for i in range(dim)]
        result = list(base)
        for i in range(dim):
            # Randomly drop with probability (1-density)
            mask_a = 1 if random.random() < self.config.density else 0
            mask_b = 1 if random.random() < self.config.density else 0
            # Rescale
            scale = 1.0 / max(self.config.density, 1e-8)
            merged_delta = self.config.interpolation * mask_a * delta_a[i] * scale + \
                          (1-self.config.interpolation) * mask_b * delta_b[i] * scale
            result[i] = base[i] + merged_delta
        return result
    def merge(self, weights_a: List[float], weights_b: List[float],
              base: Optional[List[float]] = None) -> List[float]:
        """Execute merge with configured method."""
        t = self.config.interpolation
        if self.config.method == "linear":
            return self.linear_merge(weights_a, weights_b, t)
        elif self.config.method == "slerp":
            return self.slerp_merge(weights_a, weights_b, t)
        elif self.config.method == "ties":
            if base is None: base = [0.0] * len(weights_a)
            return self.ties_merge([weights_a, weights_b], base)
        elif self.config.method == "dare":
            if base is None: base = [0.0] * len(weights_a)
            return self.dare_merge(weights_a, weights_b, base)
        else:
            raise ValueError(f"Unknown merge method: {self.config.method}")
