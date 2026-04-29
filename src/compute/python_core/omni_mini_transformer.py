# Omni LLM-from-Scratch Mini Transformer
# Ref: FareedKhan-dev/create-million-parameter-llm-from-scratch
import math
from typing import List, Dict

def rotary_position_embedding(dim: int, seq_len: int, base: float = 10000.0) -> List[List[float]]:
    inv_freq = [1.0 / (base ** (2*i / dim)) for i in range(dim // 2)]
    embeddings = []
    for pos in range(seq_len):
        row = []
        for freq in inv_freq:
            row.extend([math.cos(pos * freq), math.sin(pos * freq)])
        embeddings.append(row)
    return embeddings

def rms_norm(x: List[float], eps: float = 1e-6) -> List[float]:
    rms = math.sqrt(sum(v*v for v in x) / max(len(x), 1) + eps)
    return [round(v / rms, 8) for v in x]

def swiglu(x: List[float], gate: List[float]) -> List[float]:
    def silu(v): return v / (1 + math.exp(-min(max(v, -500), 500)))
    return [round(silu(g) * v, 8) for g, v in zip(gate, x)]

def scaled_dot_product_attention(q: List[float], k: List[float], v: List[float]) -> List[float]:
    d = len(q)
    score = sum(qi * ki for qi, ki in zip(q, k)) / math.sqrt(d)
    weight = 1 / (1 + math.exp(-min(max(score, -500), 500)))
    return [round(weight * vi, 8) for vi in v]
