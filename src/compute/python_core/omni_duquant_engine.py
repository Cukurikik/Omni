# Omni DuQuant Quantization Engine
# Ref: Hsu1023/DuQuant — NeurIPS'24 Oral | MIT
# Dual Transformation for distributing outliers in quantized LLMs
import math
from typing import List, Dict, Tuple

def hadamard_rotation(x: List[float]) -> List[float]:
    """Apply Hadamard-like rotation to distribute outliers."""
    n = len(x)
    if n == 0:
        return []
    factor = 1.0 / math.sqrt(n)
    result = []
    for i in range(n):
        val = 0.0
        for j in range(n):
            sign = 1 if bin(i & j).count('1') % 2 == 0 else -1
            val += sign * x[j]
        result.append(round(val * factor, 8))
    return result

def compute_outlier_ratio(weights: List[float], threshold_std: float = 3.0) -> Dict:
    """Compute outlier ratio before/after transformation."""
    n = len(weights)
    if n == 0:
        return {"outlier_ratio": 0, "mean": 0, "std": 0}
    mean = sum(weights) / n
    std = math.sqrt(sum((w - mean)**2 for w in weights) / n) or 1e-8
    outliers = sum(1 for w in weights if abs(w - mean) > threshold_std * std)
    return {"outlier_ratio": round(outliers / n, 6), "mean": round(mean, 6),
            "std": round(std, 6), "n_outliers": outliers}

def symmetric_quantize(value: float, n_bits: int = 4) -> int:
    """Symmetric uniform quantization to n_bits."""
    qmax = (1 << (n_bits - 1)) - 1
    return max(-qmax, min(qmax, round(value * qmax)))

def quantize_tensor(weights: List[float], n_bits: int = 4) -> Dict:
    """Quantize weights with DuQuant dual transformation pipeline."""
    rotated = hadamard_rotation(weights[:min(len(weights), 64)])
    pre_outlier = compute_outlier_ratio(weights)
    post_outlier = compute_outlier_ratio(rotated)
    scale = max(abs(v) for v in rotated) if rotated else 1.0
    normalized = [v / (scale or 1.0) for v in rotated]
    quantized = [symmetric_quantize(v, n_bits) for v in normalized]
    qmax = (1 << (n_bits - 1)) - 1
    dequantized = [q * scale / qmax for q in quantized]
    mse = sum((a - b)**2 for a, b in zip(rotated, dequantized)) / max(len(rotated), 1)
    return {"quantized": quantized[:20], "scale": round(scale, 6),
            "mse": round(mse, 8), "pre_outlier_ratio": pre_outlier["outlier_ratio"],
            "post_outlier_ratio": post_outlier["outlier_ratio"], "n_bits": n_bits}

def duquant_calibrate(layers_weights: List[List[float]], n_bits: int = 4) -> Dict:
    """Calibrate DuQuant across multiple layers."""
    results = [quantize_tensor(lw, n_bits) for lw in layers_weights]
    avg_mse = sum(r["mse"] for r in results) / max(len(results), 1)
    avg_reduction = sum(r["pre_outlier_ratio"] - r["post_outlier_ratio"] for r in results) / max(len(results), 1)
    return {"n_layers": len(results), "avg_mse": round(avg_mse, 8),
            "avg_outlier_reduction": round(avg_reduction, 6)}
