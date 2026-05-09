import torch
import torch.nn as nn
from typing import Dict, Any

class FullStackTransformerEngine(nn.Module):
    """
    Full Stack Transformer: End-to-end transformer models training, inference and serving.
    """
    def __init__(self, vocab_size: int = 50257, d_model: int = 768):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)
        self.transformer = nn.Transformer(
            d_model=d_model, 
            nhead=12, 
            num_encoder_layers=6, 
            num_decoder_layers=6,
            batch_first=True
        )
        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, src: torch.Tensor, tgt: torch.Tensor) -> Dict[str, Any]:
        try:
            src_emb = self.embed(src)
            tgt_emb = self.embed(tgt)
            out = self.transformer(src_emb, tgt_emb)
            logits = self.fc_out(out)
            return {"status": "success", "logits": logits}
        except Exception as e:
            return {"status": "error", "message": str(e)}
