import numpy as np
import faiss
from typing import List, Dict, Any

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class FaissVectorRetriever:
    def __init__(self, d: int = 768):
        self.d = d
        self.index = faiss.IndexFlatIP(d) # Inner product for cosine sim (if normalized)
        self.metadata_store = {}
        self._current_id = 0

    def add_vectors(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]) -> OmniResult:
        try:
            if vectors.shape[1] != self.d:
                return OmniResult.err(f"Dimension mismatch: expected {self.d}, got {vectors.shape[1]}")
            if len(vectors) != len(metadatas):
                return OmniResult.err("Vectors and metadata must have same length")
                
            faiss.normalize_L2(vectors)
            self.index.add(np.ascontiguousarray(vectors, dtype=np.float32))
            
            for meta in metadatas:
                self.metadata_store[self._current_id] = meta
                self._current_id += 1
                
            return OmniResult.ok(len(vectors))
        except Exception as e:
            return OmniResult.err(f"Failed to add vectors: {str(e)}")

    def retrieve(self, query: np.ndarray, top_k: int = 5) -> OmniResult:
        try:
            if query.shape[1] != self.d:
                return OmniResult.err(f"Dimension mismatch: expected {self.d}, got {query.shape[1]}")
                
            faiss.normalize_L2(query)
            D, I = self.index.search(np.ascontiguousarray(query, dtype=np.float32), top_k)
            
            results = []
            for i in range(len(query)):
                q_res = []
                for j in range(top_k):
                    idx = I[i][j]
                    if idx != -1:
                        q_res.append({
                            "score": float(D[i][j]),
                            "metadata": self.metadata_store.get(idx, {})
                        })
                results.append(q_res)
                
            return OmniResult.ok(results)
        except Exception as e:
            return OmniResult.err(f"Retrieval failed: {str(e)}")
