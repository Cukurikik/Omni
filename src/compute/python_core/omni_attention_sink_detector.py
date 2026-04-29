# Omni Attention Sink Detector (Python)
# Compute Layer: Empirical detection of attention sink emergence in language models.
# Ref: sail-sg/Attention-Sink — ICLR 2025 Spotlight.

from typing import List, Dict, Tuple
import math

class AttentionSinkResult:
    __slots__ = ('layer_idx', 'token_position', 'sink_magnitude', 'is_sink')
    def __init__(self, layer_idx: int, token_position: int, sink_magnitude: float, is_sink: bool):
        self.layer_idx = layer_idx
        self.token_position = token_position
        self.sink_magnitude = sink_magnitude
        self.is_sink = is_sink

def detect_attention_sinks(
    attention_weights: List[List[float]],
    sink_threshold: float = 0.5,
    initial_tokens: int = 4
) -> List[AttentionSinkResult]:
    results: List[AttentionSinkResult] = []
    for layer_idx, weights in enumerate(attention_weights):
        if not weights:
            continue
        for pos in range(min(initial_tokens, len(weights))):
            magnitude = weights[pos]
            is_sink = magnitude >= sink_threshold
            results.append(AttentionSinkResult(layer_idx, pos, round(magnitude, 8), is_sink))
    return results

def compute_sink_ratio(results: List[AttentionSinkResult]) -> float:
    if not results:
        return 0.0
    sink_count = sum(1 for r in results if r.is_sink)
    return round(sink_count / len(results), 6)
