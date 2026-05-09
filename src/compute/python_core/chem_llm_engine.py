import torch
import torch.nn as nn
from typing import List, Dict, Any

class ChemLLMEngine(nn.Module):
    """
    Large Language Models in Chemistry: Transformer for property prediction.
    """
    def __init__(self, vocab_size: int, hidden_dim: int = 512, num_classes: int = 1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=8, dim_feedforward=2048, batch_first=True),
            num_layers=6
        )
        self.predictor = nn.Linear(hidden_dim, num_classes)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> Dict[str, Any]:
        try:
            embeds = self.embedding(input_ids)
            encoded = self.encoder(embeds, src_key_padding_mask=~attention_mask.bool())
            
            # Pool over sequence
            pooled = encoded.mean(dim=1)
            prediction = self.predictor(pooled)
            return {"status": "success", "property_prediction": prediction}
        except Exception as e:
            return {"status": "error", "message": str(e), "property_prediction": None}
