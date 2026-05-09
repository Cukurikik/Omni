import numpy as np
from typing import List

# OMNI MOTHER Production Zero-Mock Vector DB Retriever
# Lightweight numpy-based cosine similarity retriever to fetch RAG context
# before passing prompts into the MoE system.

class OmnivectorRetriever:
    def __init__(self, embedding_dim: int):
        self.embedding_dim = embedding_dim
        self.documents = []
        self.embeddings = np.empty((0, embedding_dim), dtype=np.float32)

    def add_document(self, doc_text: str, embedding: np.ndarray):
        if embedding.shape != (self.embedding_dim,):
            raise ValueError(f"OMNI CRITICAL: Embedding must have dimension {self.embedding_dim}")
            
        # Normalize for fast cosine similarity via dot product
        norm = np.linalg.norm(embedding)
        normalized_emb = embedding / (norm + 1e-10)
        
        self.documents.append(doc_text)
        self.embeddings = np.vstack([self.embeddings, normalized_emb])

    def retrieve_top_k(self, query_embedding: np.ndarray, k: int = 3) -> List[str]:
        if len(self.documents) == 0:
            return []
            
        if query_embedding.shape != (self.embedding_dim,):
            raise ValueError(f"OMNI CRITICAL: Query embedding must have dimension {self.embedding_dim}")
            
        # Normalize query
        norm = np.linalg.norm(query_embedding)
        q_norm = query_embedding / (norm + 1e-10)
        
        # Cosine similarity is just dot product of normalized vectors
        similarities = np.dot(self.embeddings, q_norm)
        
        # Get Top-K indices
        k = min(k, len(self.documents))
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        results = [self.documents[i] for i in top_k_indices]
        return results
