# Omni LongCodeZip Compressor (Python)
# Compute Layer: Long context compression for code language models.
# Ref: YerbaPage/LongCodeZip — ASE 2025, Compress Long Context for Code LLMs.

from typing import List, Tuple
import hashlib

def compute_token_importance(tokens: List[str], attention_scores: List[float]) -> List[Tuple[str, float]]:
    if len(tokens) != len(attention_scores): return []
    return sorted(zip(tokens, attention_scores), key=lambda x: x[1], reverse=True)

def compress_context(tokens: List[str], scores: List[float], ratio: float = 0.5) -> List[str]:
    if not tokens or ratio <= 0: return []
    if ratio >= 1.0: return list(tokens)
    ranked = compute_token_importance(tokens, scores)
    keep = max(1, int(len(ranked) * ratio))
    kept_set = {t for t, _ in ranked[:keep]}
    return [t for t in tokens if t in kept_set]

def compute_compression_hash(original: List[str], compressed: List[str]) -> str:
    raw = f"{len(original)}:{len(compressed)}:{'|'.join(compressed[:10])}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
