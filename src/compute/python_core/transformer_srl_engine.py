import torch
import torch.nn as nn
from typing import Dict, Any

class TransformerSRLEngine(nn.Module):
    """
    Transformer-SRL: BERT based model for Semantic Role Labeling with predicate disambiguation.
    """
    def __init__(self, hidden_size: int = 768, num_labels: int = 104):
        super().__init__()
        self.srl_head = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size, num_labels)
        )

    def forward(self, text_embeddings: torch.Tensor, predicate_indices: torch.Tensor) -> Dict[str, Any]:
        try:
            b, seq_len, dim = text_embeddings.shape
            
            # Extract predicate embeddings
            batch_indices = torch.arange(b).unsqueeze(1).expand(-1, seq_len)
            pred_embeds = text_embeddings[batch_indices, predicate_indices.unsqueeze(1)]
            
            # Concatenate token and predicate embeddings
            combined = torch.cat([text_embeddings, pred_embeds.expand(-1, seq_len, -1)], dim=-1)
            
            logits = self.srl_head(combined)
            return {"status": "success", "srl_logits": logits}
        except Exception as e:
            return {"status": "error", "message": str(e)}
