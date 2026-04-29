# Omni ST-LLM Temporal Encoder (Python)
# Compute Layer: Spatial-temporal token embedding for video understanding.
# Ref: TencentARC/ST-LLM — ECCV 2024, LLMs as Temporal Learners.

from typing import List, Tuple
import math

def compute_temporal_position_encoding(seq_len: int, d_model: int) -> List[List[float]]:
    if seq_len <= 0 or d_model <= 0:
        return []
    pe: List[List[float]] = []
    for pos in range(seq_len):
        row: List[float] = []
        for i in range(d_model):
            if i % 2 == 0:
                row.append(round(math.sin(pos / (10000 ** (i / d_model))), 8))
            else:
                row.append(round(math.cos(pos / (10000 ** ((i - 1) / d_model))), 8))
        pe.append(row)
    return pe

def aggregate_frame_features(features: List[List[float]], strategy: str = 'mean') -> List[float]:
    if not features:
        return []
    d = len(features[0])
    if strategy == 'mean':
        return [round(sum(f[i] for f in features) / len(features), 8) for i in range(d)]
    elif strategy == 'max':
        return [round(max(f[i] for f in features), 8) for i in range(d)]
    return features[0]
