"""OMNI Compute — AWQ (Activation-Aware Weight Quantization)"""
import logging, math; from dataclasses import dataclass; from typing import List, Dict
logger = logging.getLogger("omni.awq")

@dataclass
class AWQConfig:
    bits: int = 4; group_size: int = 128; zero_point: bool = True
    version: str = "gemm"  # gemm | gemv

class OmniAWQ:
    """Activation-aware weight quantization preserving salient channels."""
    def __init__(self, c: AWQConfig): self.config = c; self.scales: Dict[str, List[float]] = {}
    def compute_channel_saliency(self, activations: List[List[float]]) -> List[float]:
        if not activations: return []
        n = len(activations[0])
        return [sum(abs(a[i]) for a in activations) / len(activations) for i in range(n)]
    def compute_scales(self, saliency: List[float], name: str) -> List[float]:
        max_s = max(saliency) if saliency else 1.0
        scales = [max(s / max_s, 0.01) for s in saliency]
        self.scales[name] = scales; return scales
    def quantize_with_scales(self, weights: List[float], scales: List[float]) -> Dict:
        scaled = [w * s for w, s in zip(weights, scales)]
        max_q = (1 << self.config.bits) - 1
        w_min, w_max = min(scaled), max(scaled)
        scale = (w_max - w_min) / max_q if w_max != w_min else 1.0
        zero = -w_min / scale if self.config.zero_point else 0.0
        qvals = [max(0, min(max_q, round(v / scale + zero))) for v in scaled]
        deq = [(q - zero) * scale / s for q, s in zip(qvals, scales)]
        err = sum((o - d)**2 for o, d in zip(weights, deq)) / max(len(weights), 1)
        return {"quantized": qvals, "scale": scale, "zero": zero, "error": err}
    def summary(self) -> Dict:
        return {"bits": self.config.bits, "layers_scaled": len(self.scales)}
