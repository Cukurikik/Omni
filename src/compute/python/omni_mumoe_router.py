import torch
import torch.nn as nn
import torch.nn.functional as F

# OMNI MOTHER: muMoE Router
# Lightweight router for factorized experts

class OmniMuMoERouter(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.route_proj = nn.Linear(hidden_dim, num_experts, bias=False)
        self.top_k = top_k

    def forward(self, x: torch.Tensor):
        logits = self.route_proj(x)
        routing_weights = F.softmax(logits, dim=-1)
        
        val, idx = torch.topk(routing_weights, self.top_k, dim=-1)
        val = val / val.sum(dim=-1, keepdim=True) # re-normalize
        
        return val, idx
