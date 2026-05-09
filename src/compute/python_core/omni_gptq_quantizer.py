"""
OMNI Compute — GPTQ Quantizer
Post-training quantization for model compression.
"""
import logging, time, math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("omni.quantizer")

@dataclass
class QuantConfig:
    bits: int = 4           # 2, 3, 4, 8
    group_size: int = 128
    sym: bool = True        # symmetric quantization
    desc_act: bool = False  # order-preserving quantization
    damp_percent: float = 0.01

class QuantStats:
    def __init__(self):
        self.layers_quantized = 0
        self.total_params = 0
        self.quantized_params = 0
        self.total_error = 0.0
    def add(self, original_size: int, quantized_size: int, error: float):
        self.layers_quantized += 1
        self.total_params += original_size
        self.quantized_params += quantized_size
        self.total_error += error
    @property
    def compression_ratio(self) -> float:
        return self.total_params / max(self.quantized_params, 1)
    @property
    def avg_error(self) -> float:
        return self.total_error / max(self.layers_quantized, 1)
    def summary(self) -> Dict:
        return {"layers": self.layers_quantized, "compression": f"{self.compression_ratio:.2f}x",
                "avg_error": f"{self.avg_error:.6f}",
                "original_mb": self.total_params * 4 / (1024*1024),
                "quantized_mb": self.quantized_params * (4 / 8) / (1024*1024)}

class OmniQuantizer:
    """Post-training quantization engine."""
    def __init__(self, config: QuantConfig):
        self.config = config
        self.stats = QuantStats()
    def compute_scales_zeros(self, weight_col: List[float]) -> Tuple[float, float]:
        """Compute quantization scale and zero-point for a column."""
        w_min = min(weight_col); w_max = max(weight_col)
        max_q = (1 << self.config.bits) - 1
        if self.config.sym:
            abs_max = max(abs(w_min), abs(w_max))
            scale = abs_max / (max_q // 2) if abs_max > 0 else 1.0
            zero = 0.0
        else:
            scale = (w_max - w_min) / max_q if (w_max - w_min) > 0 else 1.0
            zero = -w_min / scale
        return scale, zero
    def quantize_column(self, values: List[float], scale: float, zero: float) -> List[int]:
        """Quantize a column of weights."""
        max_q = (1 << self.config.bits) - 1
        return [max(0, min(max_q, round(v / scale + zero))) for v in values]
    def dequantize_column(self, qvals: List[int], scale: float, zero: float) -> List[float]:
        """Dequantize back to float."""
        return [(q - zero) * scale for q in qvals]
    def compute_error(self, original: List[float], reconstructed: List[float]) -> float:
        """MSE between original and reconstructed weights."""
        return sum((a - b) ** 2 for a, b in zip(original, reconstructed)) / max(len(original), 1)
    def quantize_layer(self, weights: List[List[float]], layer_name: str) -> Dict:
        """Quantize an entire weight matrix."""
        start = time.time()
        rows = len(weights); cols = len(weights[0]) if weights else 0
        total_error = 0.0
        quantized = []
        scales, zeros = [], []
        for j in range(cols):
            col = [weights[i][j] for i in range(rows)]
            s, z = self.compute_scales_zeros(col)
            qcol = self.quantize_column(col, s, z)
            dcol = self.dequantize_column(qcol, s, z)
            total_error += self.compute_error(col, dcol)
            quantized.append(qcol); scales.append(s); zeros.append(z)
        avg_err = total_error / max(cols, 1)
        self.stats.add(rows * cols, rows * cols, avg_err)
        elapsed = time.time() - start
        logger.info(f"Quantized {layer_name}: {rows}x{cols} -> {self.config.bits}bit, err={avg_err:.6f}, {elapsed:.2f}s")
        return {"layer": layer_name, "shape": [rows, cols], "bits": self.config.bits,
                "error": avg_err, "time_sec": elapsed}
    def get_summary(self) -> Dict:
        return self.stats.summary()
