# moe_vision_language_expert.py — Compute
# Layer: Compute — Vision-Language Expert Processor
# Inspired by: CompeteSMoE (Vision Language)

import torch
import torch.nn as nn
from typing import Optional

class VisionLanguageExpert(nn.Module):
    """
    A specialized MoE expert that projects Vision tokens (from ViT/CLIP) and 
    Text tokens into a shared semantic space for multimodal reasoning.
    """
    def __init__(self, hidden_dim: int = 4096, intermediate_dim: int = 14336):
        super().__init__()
        # SwiGLU FFN
        self.gate_proj = nn.Linear(hidden_dim, intermediate_dim, bias=False)
        self.up_proj = nn.Linear(hidden_dim, intermediate_dim, bias=False)
        self.down_proj = nn.Linear(intermediate_dim, hidden_dim, bias=False)
        self.act_fn = nn.SiLU()
        
        # Modality embedding to differentiate text vs vision tokens
        self.modality_emb = nn.Embedding(2, hidden_dim) # 0: Text, 1: Vision

    def forward(self, hidden_states: torch.Tensor, modality_ids: torch.Tensor) -> torch.Tensor:
        """
        hidden_states: [batch_size, seq_len, hidden_dim]
        modality_ids: [batch_size, seq_len] containing 0s and 1s
        """
        # Inject modality embeddings
        modality_shift = self.modality_emb(modality_ids)
        x = hidden_states + modality_shift
        
        # SwiGLU computation
        gate = self.act_fn(self.gate_proj(x))
        up = self.up_proj(x)
        output = self.down_proj(gate * up)
        
        return output
