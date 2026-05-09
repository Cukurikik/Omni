import torch
import torch.nn as nn

# OMNI MOTHER: CLIP-MoE Text Encoder
# Implements MoE layers within the Transformer blocks of CLIP text encoder

class OmniCLIPTextMoE(nn.Module):
    def __init__(self, embed_dim: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.router = nn.Linear(embed_dim, num_experts, bias=False)
        self.experts = nn.ModuleList([
            nn.Sequential(nn.Linear(embed_dim, embed_dim * 4), nn.GELU(), nn.Linear(embed_dim * 4, embed_dim))
            for _ in range(num_experts)
        ])
        self.top_k = top_k

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x is text tokens [batch, seq_len, embed_dim]
        logits = self.router(x)
        weights, indices = torch.topk(torch.softmax(logits, dim=-1), self.top_k, dim=-1)
        weights = weights / weights.sum(dim=-1, keepdim=True)
        
        out = torch.zeros_like(x)
        for i in range(self.top_k):
            expert_idx = indices[:, :, i]
            weight = weights[:, :, i]
            
            for e_idx, expert in enumerate(self.experts):
                mask = (expert_idx == e_idx)
                if mask.any():
                    out[mask] += weight[mask].unsqueeze(-1) * expert(x[mask])
                    
        return out
