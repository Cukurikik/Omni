# Omni SuperKnowa Enterprise RAG Pipeline
# Ref: ibm-self-serve-assets/SuperKnowa — Apache-2.0
# Implements: Retriever -> Reranker -> Generator -> Evaluator modular pipeline
import math
from typing import List, Dict, Tuple

def bm25_score(query_terms: List[str], doc_terms: List[str], doc_len: int,
               avg_dl: float, k1: float = 1.5, b: float = 0.75) -> float:
    score = 0.0
    for qt in query_terms:
        tf = doc_terms.count(qt)
        idf = math.log(1.0 + 1.0)  # simplified single-doc IDF
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * doc_len / max(avg_dl, 1))
        score += idf * numerator / max(denominator, 1e-9)
    return round(score, 6)

def rerank_by_cross_score(query_emb: List[float], doc_embs: List[Tuple[str, List[float]]]) -> List[Tuple[str, float]]:
    results = []
    for doc_id, emb in doc_embs:
        dot = sum(a * b for a, b in zip(query_emb, emb))
        na = math.sqrt(sum(a * a for a in query_emb)) or 1
        nb = math.sqrt(sum(b * b for b in emb)) or 1
        results.append((doc_id, round(dot / (na * nb), 8)))
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def context_adherence_score(response_tokens: List[str], context_tokens: List[str]) -> float:
    if not response_tokens: return 0.0
    ctx_set = set(context_tokens)
    overlap = sum(1 for t in response_tokens if t in ctx_set)
    return round(overlap / len(response_tokens), 6)

def hallucination_rate(adherence: float) -> float:
    return round(max(0, 1.0 - adherence), 6)
