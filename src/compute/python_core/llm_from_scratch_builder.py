import torch
import torch.nn as nn
from typing import Dict, Any

class LLMFromScratchEngine(nn.Module):
    """
    Building LLMs from scratch: GPT-style architecture.
    """
    def __init__(self, vocab_size: int = 50257, d_model: int = 768, num_heads: int = 12, num_layers: int = 12):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(1024, d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=num_heads, batch_first=True)
        self.blocks = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, idx: torch.Tensor) -> Dict[str, Any]:
        try:
            b, t = idx.size()
            pos = torch.arange(0, t, dtype=torch.long, device=idx.device)
            x = self.token_emb(idx) + self.pos_emb(pos)
            
            # Causal mask
            mask = torch.triu(torch.ones(t, t, device=idx.device), diagonal=1).bool()
            x = self.blocks(x, mask=mask)
            logits = self.lm_head(x)
            
            return {"status": "success", "logits": logits}
        except Exception as e:
            return {"status": "error", "message": str(e)}
