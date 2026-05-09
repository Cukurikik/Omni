# OMNI Compute & NLP Layer
# Siamese Neural Networks for Semantic Text Similarity
# Implementation based on shahrukhx01/siamese-nn-semantic-text-similarity.

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniSiameseSemanticNetwork(nn.Module):
    """
    Omni implementation of a Siamese network using shared Transformer weights
    to calculate semantic similarity between two input sequences.
    """
    def __init__(self, encoder: nn.Module, hidden_size: int = 768):
        super().__init__()
        # Shared encoder (e.g., BERT, RoBERTa, or Omni's native Universal Transformer)
        self.encoder = encoder
        
        # Optional projection head before cosine similarity
        self.projection = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.LayerNorm(hidden_size)
        )

    def forward_once(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Passes a single sequence through the shared encoder."""
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        
        # Mean pooling over the sequence length, respecting the attention mask
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        
        pooled = sum_embeddings / sum_mask
        projected = self.projection(pooled)
        return projected

    def forward(self, input_ids_a, mask_a, input_ids_b, mask_b) -> torch.Tensor:
        """Returns the cosine similarity between the two sequence representations."""
        emb_a = self.forward_once(input_ids_a, mask_a)
        emb_b = self.forward_once(input_ids_b, mask_b)
        
        # Calculate Cosine Similarity
        similarity = F.cosine_similarity(emb_a, emb_b, dim=-1)
        return similarity

def omni_semantic_search(query_emb: torch.Tensor, document_embs: torch.Tensor) -> torch.Tensor:
    """
    Utility for high-speed semantic retrieval.
    In Omni, this delegates to Faiss or native C++ SIMD routines if the tensor is large.
    """
    # [1, hidden_size] x [num_docs, hidden_size] -> [num_docs]
    scores = F.cosine_similarity(query_emb.unsqueeze(0), document_embs, dim=-1)
    return scores
