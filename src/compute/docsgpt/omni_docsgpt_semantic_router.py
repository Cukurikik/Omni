# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# DocsGPT Semantic Router (OMNI Zero-Mock Implementation)
# Implements Cosine Distance similarity-based Document RAG selection.

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class Result:
    value: Optional[List[int]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[int]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class SemanticRouter:
    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(x * y for x, y in zip(v1, v2))
        norm_v1 = math.sqrt(sum(x * x for x in v1))
        norm_v2 = math.sqrt(sum(y * y for y in v2))
        return dot / (norm_v1 * norm_v2 + 1e-10)

    def top_k_documents(self, query_emb: List[float], doc_embeddings: List[List[float]], k: int) -> Result:
        if not doc_embeddings:
            return Result.err("Document embedding database is empty.")
        if k <= 0:
            return Result.err("Top-K must be greater than zero.")
        if len(query_emb) != len(doc_embeddings[0]):
            return Result.err("Dimension mismatch between query and database.")

        scores = []
        for idx, doc_emb in enumerate(doc_embeddings):
            sim = self.cosine_similarity(query_emb, doc_emb)
            scores.append((sim, idx))

        # Sort descending by similarity
        scores.sort(key=lambda x: x[0], reverse=True)
        top_indices = [idx for _, idx in scores[:k]]
        
        return Result.ok(top_indices)
