# OMNI Compute Layer - LlamaIndex Retriever
import numpy as np

class RetrieveError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def retrieve_top_k(query_vec: np.ndarray, index_matrix: np.ndarray, k: int) -> Result:
    """Retrieves top-k documents using cosine similarity."""
    try:
        if k <= 0 or len(index_matrix) == 0:
            return Result(error=RetrieveError("Invalid indices or K value"))
            
        scores = np.dot(index_matrix, query_vec)
        top_indices = np.argsort(scores)[-k:][::-1]
        
        return Result(value={"indices": top_indices.tolist(), "scores": scores[top_indices].tolist()})
    except Exception as e:
        return Result(error=RetrieveError(f"Retrieval failed: {str(e)}"))
