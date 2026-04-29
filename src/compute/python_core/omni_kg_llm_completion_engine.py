# Omni KG-LLM Completion Engine (Python)
# Compute Layer: Knowledge graph completion using LLM triplet prediction.
# Ref: yao8839836/kg-llm — ICASSP 2025.

from typing import List, Dict, Tuple, Optional
import hashlib

class KGTriple:
    __slots__ = ('head', 'relation', 'tail', 'score')
    def __init__(self, head: str, relation: str, tail: str, score: float = 0.0):
        self.head = head
        self.relation = relation
        self.tail = tail
        self.score = score

def predict_tail(head: str, relation: str, candidates: List[str], scores: List[float]) -> Optional[KGTriple]:
    if len(candidates) != len(scores) or not candidates:
        return None
    max_idx = scores.index(max(scores))
    return KGTriple(head, relation, candidates[max_idx], round(scores[max_idx], 8))

def evaluate_hits_at_k(predictions: List[KGTriple], gold: Dict[str, str], k: int = 10) -> float:
    if not predictions or not gold:
        return 0.0
    hits = 0
    ranked = sorted(predictions, key=lambda t: t.score, reverse=True)[:k]
    for t in ranked:
        key = f"{t.head}|{t.relation}"
        if gold.get(key) == t.tail:
            hits += 1
    return round(hits / min(k, len(gold)), 6)

def compute_triple_hash(triple: KGTriple) -> str:
    raw = f"{triple.head}|{triple.relation}|{triple.tail}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
