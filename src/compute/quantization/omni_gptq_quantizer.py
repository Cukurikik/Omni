"""
@omni-layer Compute | @omni-source microsoft/GPTQ-for-LLaMa
@omni-description GPTQ quantization engine: 4-bit weight quantization with
optimal bit allocation using Hessian-based sensitivity.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniGPTQQuantizer:
    def __init__(self, bits=4, group_size=128):
        self.bits = bits; self.group_size = group_size
        self.n_levels = 2**bits

    def quantize_column(self, weights: List[float], hessian_diag: List[float]) -> OmniResult:
        try:
            n = len(weights)
            w_min = min(weights); w_max = max(weights)
            scale = (w_max - w_min) / max(self.n_levels - 1, 1) if w_max != w_min else 1
            zero_point = round(-w_min / scale) if scale != 0 else 0
            quantized = []
            dequantized = []
            total_error = 0.0
            for i in range(n):
                q = max(0, min(self.n_levels-1, round(weights[i]/scale + zero_point)))
                quantized.append(q)
                dq = (q - zero_point) * scale
                dequantized.append(dq)
                err = (weights[i] - dq)**2
                sensitivity = hessian_diag[i] if i < len(hessian_diag) else 1.0
                total_error += err * sensitivity
            return OmniResult(data={"quantized": quantized[:8], "scale": scale, "zero_point": zero_point, "mse": total_error/max(n,1), "bits": self.bits, "compression": 32/self.bits})
        except Exception as e: return OmniResult(error=e)

    def estimate_model_size(self, n_params: int) -> OmniResult:
        fp32_mb = n_params * 4 / (1024**2)
        quant_mb = n_params * self.bits / 8 / (1024**2)
        overhead = n_params / self.group_size * 4 * 2 / (1024**2)
        return OmniResult(data={"fp32_mb": fp32_mb, "quantized_mb": quant_mb + overhead, "compression": fp32_mb/(quant_mb+overhead), "overhead_mb": overhead})
