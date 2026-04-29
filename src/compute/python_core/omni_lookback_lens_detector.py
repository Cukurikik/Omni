# Omni Lookback Lens Hallucination Detector (Python)
# Compute Layer: Attention-based contextual hallucination detection.
# Ref: voidism/Lookback-Lens — EMNLP 2024, Hallucination via Attention Maps.

from typing import List, Tuple
import math

def compute_lookback_ratio(attention_weights: List[List[float]], context_len: int) -> List[float]:
    ratios: List[float] = []
    for layer_weights in attention_weights:
        if not layer_weights or context_len <= 0: ratios.append(0.0); continue
        context_attn = sum(layer_weights[:min(context_len, len(layer_weights))])
        total_attn = sum(layer_weights)
        ratios.append(round(context_attn / total_attn, 8) if total_attn > 0 else 0.0)
    return ratios

def detect_hallucination(lookback_ratios: List[float], threshold: float = 0.1) -> bool:
    if not lookback_ratios: return True
    avg = sum(lookback_ratios) / len(lookback_ratios)
    return avg < threshold

def train_linear_classifier(features: List[List[float]], labels: List[int]) -> List[float]:
    if not features or len(features) != len(labels): return []
    d = len(features[0])
    weights = [0.0] * d
    lr = 0.01
    for _ in range(100):
        for x, y in zip(features, labels):
            pred = sum(w * xi for w, xi in zip(weights, x))
            err = y - pred
            weights = [w + lr * err * xi for w, xi in zip(weights, x)]
    return [round(w, 8) for w in weights]
