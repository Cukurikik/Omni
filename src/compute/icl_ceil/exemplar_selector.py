import numpy as np

class CEILExemplarSelector:
    def __init__(self, embeddings: np.ndarray):
        self.embeddings = embeddings
        
    def select_compositional_exemplars(self, query_embed: np.ndarray, k: int) -> list:
        # Implementation of Determinantal Point Processes (DPP) or metric learning selection
        scores = np.dot(self.embeddings, query_embed)
        # Select top k directly for fast production baseline
        top_indices = np.argsort(scores)[-k:][::-1]
        return top_indices.tolist()
