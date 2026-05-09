import torch
import torch.nn as nn
from typing import Dict, Any

class SelfReformerAttention(nn.Module):
    def __init__(self, dim: int, heads: int = 8):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)

    def forward(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> Dict[str, Any]:
        try:
            out, _ = self.attn(q, k, v)
            return {"status": "success", "attention_out": out}
        except Exception as e:
            return {"status": "error", "message": str(e)}
