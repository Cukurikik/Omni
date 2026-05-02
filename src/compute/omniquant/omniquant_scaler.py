"""
@omni-domain Compute Layer (Quantization)
@omni-source OpenGVLab/OmniQuant
@omni-description OmniQuant Scaler mimicking weight-only quantization scaling.
@omni-requirement zero-mock, monadic-error
"""
import math
from typing import Any, Optional, List

class OmniResult:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error
    def is_ok(self): return self.error is None

class QuantError(Exception): pass

class OmniQuantScaler:
    def __init__(self, bits=4, group_size=128):
        self.bits = bits
        self.group_size = group_size
        self.qmin = 0
        self.qmax = (1 << bits) - 1

    def compute_scale_zero(self, weights: List[float]) -> OmniResult:
        try:
            if not weights:
                return OmniResult(error=QuantError("Weights empty."))
            w_min = min(weights)
            w_max = max(weights)
            scale = (w_max - w_min) / self.qmax if self.qmax > 0 else 1.0
            zero_point = round(-w_min / scale) if scale != 0 else 0
            zero_point = max(self.qmin, min(self.qmax, zero_point))
            return OmniResult(data={"scale": scale, "zero_point": zero_point})
        except Exception as e:
            return OmniResult(error=QuantError(f"Scale computation failed: {e}"))

    def quantize(self, weights: List[float]) -> OmniResult:
        try:
            if not weights:
                return OmniResult(error=QuantError("Weights empty."))
            groups = [weights[i:i+self.group_size] for i in range(0, len(weights), self.group_size)]
            quantized = []
            scales = []
            zeros = []
            for group in groups:
                sz = self.compute_scale_zero(group)
                if not sz.is_ok(): return sz
                s, z = sz.data["scale"], sz.data["zero_point"]
                scales.append(s)
                zeros.append(z)
                for w in group:
                    q = round(w / s + z) if s != 0 else z
                    q = max(self.qmin, min(self.qmax, q))
                    quantized.append(q)
            return OmniResult(data={"quantized": quantized, "scales": scales, "zeros": zeros, "bits": self.bits})
        except Exception as e:
            return OmniResult(error=QuantError(f"Quantization failed: {e}"))

    def dequantize(self, quantized: List[int], scales: List[float], zeros: List[int]) -> OmniResult:
        try:
            if not quantized:
                return OmniResult(error=QuantError("Quantized data empty."))
            result = []
            for i, q in enumerate(quantized):
                group_idx = i // self.group_size
                s = scales[group_idx]
                z = zeros[group_idx]
                result.append((q - z) * s)
            return OmniResult(data={"dequantized": result})
        except Exception as e:
            return OmniResult(error=QuantError(f"Dequantization failed: {e}"))
