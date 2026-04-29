# Omni Flora Gradient Compressor
# Ref: BorealisAI/flora-opt — ICML 2024
# Implements: Random projection gradient compression, high-rank updates, momentum transfer
import math
from typing import List, Dict

def random_projection_compress(gradient: List[float], proj_dim: int, seed: int = 42) -> List[float]:
    d = len(gradient)
    compressed = [0.0] * proj_dim
    for i in range(d):
        h = ((seed * (i + 1) * 2654435761) >> 16) % proj_dim
        sign = 1.0 if ((seed * (i + 1) * 2246822519) >> 17) % 2 == 0 else -1.0
        compressed[h] += gradient[i] * sign / math.sqrt(proj_dim)
    return [round(c, 8) for c in compressed]

def decompress(compressed: List[float], orig_dim: int, proj_dim: int, seed: int = 42) -> List[float]:
    result = [0.0] * orig_dim
    for i in range(orig_dim):
        h = ((seed * (i + 1) * 2654435761) >> 16) % proj_dim
        sign = 1.0 if ((seed * (i + 1) * 2246822519) >> 17) % 2 == 0 else -1.0
        result[i] = compressed[h] * sign * math.sqrt(proj_dim)
    return [round(r, 8) for r in result]

def flora_update(params: List[float], gradient: List[float], lr: float = 0.001,
                  proj_dim: int = 64, seed: int = 42) -> List[float]:
    compressed = random_projection_compress(gradient, proj_dim, seed)
    decompressed = decompress(compressed, len(params), proj_dim, seed)
    return [round(p - lr * g, 8) for p, g in zip(params, decompressed)]

def momentum_transfer(old_momentum: List[float], old_seed: int, new_seed: int,
                       proj_dim: int, orig_dim: int) -> List[float]:
    expanded = decompress(old_momentum, orig_dim, proj_dim, old_seed)
    return random_projection_compress(expanded, proj_dim, new_seed)
