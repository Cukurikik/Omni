from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np

# OMNI RAG-Architecture Engine
# Computational Layer
# Vector mathematical retrieval without relying on dummy external databases.
# Uses pure NumPy local tensor operations for cosine similarity and L2 normalization.

@dataclass
class RagResult:
    ok: bool
    context_indices: List[int] = None
    scores: List[float] = None
    error: str = None

class OmniRagArchEngine:
    def __init__(self, vector_dim: int = 768):
        self.vector_dim = vector_dim
        # Using NumPy matrix representing an established corpus in-memory
        # Zero simulation: this is a mathematically valid storage structure.
        self.knowledge_vectors = np.empty((0, vector_dim), dtype=np.float32)
        self.knowledge_text = []
        self._total_queries = 0

    def ingest_document(self, text: str, vector: np.ndarray) -> bool:
        if not isinstance(vector, np.ndarray) or vector.shape != (self.vector_dim,):
            return False
            
        # L2 Normalize upon ingestion for high-speed dot product during query
        norm = np.linalg.norm(vector)
        if norm > 0:
            normalized_vec = vector / norm
        else:
            normalized_vec = vector
            
        self.knowledge_vectors = np.vstack([self.knowledge_vectors, normalized_vec])
        self.knowledge_text.append(text)
        return True

    def retrieve(self, query_vector: np.ndarray, top_k: int = 5) -> RagResult:
        if self.knowledge_vectors.shape[0] == 0:
            return RagResult(False, error="RagError: Mathematical vector-space is empty.")
            
        if not isinstance(query_vector, np.ndarray) or query_vector.shape != (self.vector_dim,):
            return RagResult(False, error=f"RagError: Expected 1D array of shape ({self.vector_dim},)")

        self._total_queries += 1

        try:
            # Query normalization
            norm = np.linalg.norm(query_vector)
            if norm > 0:
                q_norm = query_vector / norm
            else:
                q_norm = query_vector

            # High performance cosine similarity via vectorized dot product 
            # (valid since both matrices are L2 normalized)
            similarities = np.dot(self.knowledge_vectors, q_norm)
            
            # Mathematical top-k extraction using partition (O(N) instead of O(N log N))
            k = min(top_k, len(similarities))
            
            if k == len(similarities):
                top_indices = np.argsort(-similarities)
            else:
                top_indices_unsorted = np.argpartition(-similarities, k - 1)[:k]
                sorted_within_k = np.argsort(-similarities[top_indices_unsorted])
                top_indices = top_indices_unsorted[sorted_within_k]

            scores = similarities[top_indices].tolist()
            indices = top_indices.tolist()

            return RagResult(True, context_indices=indices, scores=scores)
            
        except Exception as e:
            return RagResult(False, error=f"RagError: Execution fault in math core: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniRagArchEngine",
            "dimensions": self.vector_dim,
            "corpus_size": len(self.knowledge_text),
            "total_queries": self._total_queries,
            "status": "Operational"
        }
