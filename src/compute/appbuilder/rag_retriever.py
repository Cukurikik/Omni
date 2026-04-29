import numpy as np
from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class RAGRetriever:
    def retrieve_context(self, query_emb: np.ndarray, doc_embs: np.ndarray) -> OmniResult:
        if query_emb is None or doc_embs is None:
            return OmniResult(None, "Embeddings missing")
            
        try:
            # Python high-performance vector search for AppBuilder RAG
            similarities = np.dot(doc_embs, query_emb) / (
                np.linalg.norm(doc_embs, axis=1) * np.linalg.norm(query_emb) + 1e-8
            )
            top_k_idx = np.argsort(similarities)[-5:][::-1]
            
            return OmniResult(top_k_idx.tolist())
        except Exception as e:
            return OmniResult(None, str(e))
