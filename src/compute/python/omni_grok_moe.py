import torch
import torch.nn as nn

# OMNI MOTHER: Grok-style Sparse MoE
# High parameter count, extreme sparsity (top-2 routing)

class OmniGrokMoE(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int = 8, top_k: int = 2):
        super().__init__()
        self.router = nn.Linear(hidden_dim, num_experts, bias=False)
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim * 4),
                nn.GELU(),
                nn.Linear(hidden_dim * 4, hidden_dim)
            ) for _ in range(num_experts)
        ])
        self.top_k = top_k

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.router(x)
        topk_probs, topk_indices = torch.topk(torch.softmax(logits, dim=-1), self.top_k, dim=-1)
        
        final_output = torch.zeros_like(x)
        
        # Iterate over k
        for k in range(self.top_k):
            indices_k = topk_indices[..., k]
            probs_k = topk_probs[..., k]
            
            for i, expert in enumerate(self.experts):
                mask = (indices_k == i)
                if mask.any():
                    final_output[mask] += expert(x[mask]) * probs_k[mask].unsqueeze(-1)
                    
        return final_output
