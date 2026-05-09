"""
@omni-layer Compute | @omni-source md-experiments/elastic_transformers
@omni-description Semantic search engine: dense retrieval with sentence
transformers, BM25 hybrid scoring, and re-ranking pipeline.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniSemanticSearch:
    def __init__(self, d=384):
        self.d = d; self.docs: List[Dict] = []

    def _hash_embed(self, text: str) -> List[float]:
        emb = [0.0]*self.d
        words = text.lower().split()
        for w_idx, word in enumerate(words):
            for c_idx, ch in enumerate(word):
                idx = (ord(ch) * (c_idx+1) * (w_idx+1)) % self.d
                emb[idx] += math.sin(ord(ch)*0.1) * 0.1
        norm = math.sqrt(sum(v*v for v in emb) + 1e-8)
        return [v/norm for v in emb]

    def index_document(self, doc_id: str, text: str) -> OmniResult:
        try:
            emb = self._hash_embed(text)
            words = text.lower().split()
            tf = {}
            for w in words: tf[w] = tf.get(w, 0) + 1
            self.docs.append({"id": doc_id, "text": text, "emb": emb, "tf": tf, "n_words": len(words)})
            return OmniResult(data={"indexed": doc_id, "total": len(self.docs)})
        except Exception as e: return OmniResult(error=e)

    def bm25_score(self, query_terms: List[str], doc: Dict, k1: float = 1.5, b: float = 0.75) -> float:
        avg_dl = sum(d["n_words"] for d in self.docs) / max(len(self.docs), 1)
        score = 0
        for term in query_terms:
            df = sum(1 for d in self.docs if term in d["tf"])
            idf = math.log((len(self.docs) - df + 0.5) / (df + 0.5) + 1)
            tf = doc["tf"].get(term, 0)
            tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc["n_words"] / avg_dl))
            score += idf * tf_norm
        return score

    def hybrid_search(self, query: str, top_k: int = 5, alpha: float = 0.7) -> OmniResult:
        try:
            q_emb = self._hash_embed(query)
            q_terms = query.lower().split()
            scored = []
            for doc in self.docs:
                dense = sum(q_emb[i]*doc["emb"][i] for i in range(self.d))
                sparse = self.bm25_score(q_terms, doc)
                hybrid = alpha * dense + (1 - alpha) * sparse * 0.1
                scored.append((doc["id"], hybrid, dense, sparse))
            scored.sort(key=lambda x: -x[1])
            return OmniResult(data={"results": [{"id": s[0], "hybrid_score": s[1], "dense": s[2], "bm25": s[3]} for s in scored[:top_k]], "n_docs": len(self.docs)})
        except Exception as e: return OmniResult(error=e)
