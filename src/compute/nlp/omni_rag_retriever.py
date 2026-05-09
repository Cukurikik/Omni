"""
omni_rag_retriever.py — RAG Context Retriever
Layer: Compute / NLP
Inspired by: ukairia777/pytorch-nlp-tutorial

Implements an embedding-based retriever for Retrieval-Augmented Generation (RAG).
Calculates Cosine Similarity between a query embedding and a document store
to fetch the top-k most relevant contexts. Zero mock.
"""

import torch
import torch.nn.functional as F

class OmniRAGRetriever:
    def __init__(self, device: torch.device = None):
        self.device = device if device else torch.device('cpu')
        # In a real deployed system, these would be in a Vector DB (like FAISS / Qdrant)
        # Here we implement the pure tensor logic for in-memory batch processing.
        self.doc_embeddings = None
        self.doc_texts = []

    def load_documents(self, embeddings: torch.Tensor, texts: list[str]):
        """
        Loads pre-computed document embeddings and their corresponding texts.
        embeddings: (NumDocs, EmbedDim)
        """
        assert embeddings.shape[0] == len(texts), "Embeddings count must match texts count"
        self.doc_embeddings = embeddings.to(self.device)
        # Normalize for fast cosine similarity via dot product
        self.doc_embeddings = F.normalize(self.doc_embeddings, p=2, dim=-1)
        self.doc_texts = texts

    def retrieve(self, query_embedding: torch.Tensor, top_k: int = 5) -> list[str]:
        """
        query_embedding: (EmbedDim)
        Returns the top_k document strings.
        """
        if self.doc_embeddings is None:
            raise ValueError("Document store is empty. Call load_documents first.")

        query_embedding = query_embedding.to(self.device)
        if query_embedding.dim() == 1:
            query_embedding = query_embedding.unsqueeze(0) # (1, EmbedDim)

        query_embedding = F.normalize(query_embedding, p=2, dim=-1)

        # Cosine Similarity (Since both are L2 normalized, dot product = cosine similarity)
        # (1, EmbedDim) @ (EmbedDim, NumDocs) -> (1, NumDocs)
        similarities = torch.matmul(query_embedding, self.doc_embeddings.T).squeeze(0)

        # Get Top-K indices
        k = min(top_k, similarities.shape[0])
        top_scores, top_indices = torch.topk(similarities, k)

        results = []
        for idx in top_indices.tolist():
            results.append(self.doc_texts[idx])

        return results
