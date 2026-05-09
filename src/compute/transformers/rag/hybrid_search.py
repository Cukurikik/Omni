"""
OMNI Transformer — Hybrid Search for RAG
Combine vector search with BM25 keyword search for better retrieval.
"""
import math
from typing import List, Dict, Any, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class BM25Index:
    """BM25 keyword-based search index."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[Dict[str, Any]] = []
        self.doc_freqs: Dict[str, int] = Counter()
        self.doc_lens: List[int] = []
        self.avg_doc_len: float = 0.0
        self.term_freqs: List[Dict[str, int]] = []
        self.n_docs: int = 0

    def add(self, documents: List[Dict[str, Any]]) -> None:
        for doc in documents:
            text = doc["text"].lower()
            tokens = text.split()
            tf = Counter(tokens)
            self.term_freqs.append(dict(tf))
            self.doc_lens.append(len(tokens))
            self.documents.append(doc)
            for term in set(tokens):
                self.doc_freqs[term] += 1
        self.n_docs = len(self.documents)
        self.avg_doc_len = sum(self.doc_lens) / max(self.n_docs, 1)

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        query_tokens = query.lower().split()
        scores = []
        for i in range(self.n_docs):
            score = 0.0
            for term in query_tokens:
                if term in self.term_freqs[i]:
                    tf = self.term_freqs[i][term]
                    df = self.doc_freqs.get(term, 0)
                    idf = math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1)
                    dl = self.doc_lens[i]
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * dl / self.avg_doc_len)
                    score += idf * numerator / denominator
            scores.append((i, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scores[:top_k]:
            doc = self.documents[idx].copy()
            doc["bm25_score"] = score
            results.append(doc)
        return results


class HybridSearcher:
    """Combine vector search and BM25 with reciprocal rank fusion."""
    def __init__(self, vector_index, bm25_index: Optional[BM25Index] = None,
                 vector_weight: float = 0.6, rrf_k: int = 60):
        self.vector_index = vector_index
        self.bm25_index = bm25_index or BM25Index()
        self.vector_weight = vector_weight
        self.bm25_weight = 1.0 - vector_weight
        self.rrf_k = rrf_k

    def search(self, query: str, query_embedding, top_k: int = 10) -> List[Dict[str, Any]]:
        vector_results = self.vector_index.search(query_embedding, top_k * 2)
        bm25_results = self.bm25_index.search(query, top_k * 2)

        # Reciprocal Rank Fusion
        scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict] = {}

        for rank, doc in enumerate(vector_results):
            key = doc.get("text", "")[:100]
            scores[key] = scores.get(key, 0) + self.vector_weight / (rank + self.rrf_k)
            doc_map[key] = doc

        for rank, doc in enumerate(bm25_results):
            key = doc.get("text", "")[:100]
            scores[key] = scores.get(key, 0) + self.bm25_weight / (rank + self.rrf_k)
            if key not in doc_map:
                doc_map[key] = doc

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results = []
        for key, score in ranked:
            doc = doc_map[key].copy()
            doc["hybrid_score"] = score
            results.append(doc)
        return results
