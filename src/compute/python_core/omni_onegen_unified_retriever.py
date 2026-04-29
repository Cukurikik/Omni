# Omni OneGen Unified Retriever (Python)
# Compute Layer: One-pass unified generation and retrieval for LLMs.
# Ref: zjunlp/OneGen — EMNLP 2024, Efficient OneGen.

from typing import List, Tuple
import math

def compute_retrieval_embedding(hidden_states: List[float], retrieval_token_idx: int) -> List[float]:
    if retrieval_token_idx < 0 or retrieval_token_idx >= len(hidden_states):
        return []
    return hidden_states[retrieval_token_idx:]

def dot_product_score(query: List[float], doc: List[float]) -> float:
    if len(query) != len(doc): return 0.0
    return round(sum(q * d for q, d in zip(query, doc)), 8)

def rank_by_score(query: List[float], docs: List[List[float]], top_k: int = 5) -> List[Tuple[int, float]]:
    scored = [(i, dot_product_score(query, d)) for i, d in enumerate(docs)]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
