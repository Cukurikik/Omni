import torch
import torch.nn as nn
import torch.nn.functional as F

# OMNI MOTHER: DeepSeek-style MoE
# Uses Fine-Grained Experts and Shared Isolation Experts

class OmniDeepSeekMoE(nn.Module):
    def __init__(self, hidden_dim: int, num_routed_experts: int = 64, num_shared_experts: int = 2, top_k: int = 8):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_routed_experts = num_routed_experts
        self.top_k = top_k
        
        # DeepSeek uses smaller experts, so intermediate size is smaller than standard LLaMA
        inter_dim = hidden_dim * 2 
        
        # Shared experts are always active
        self.shared_experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, inter_dim, bias=False),
                nn.SiLU(),
                nn.Linear(inter_dim, hidden_dim, bias=False)
            ) for _ in range(num_shared_experts)
        ])
        
        # Routed experts
        self.routed_experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, inter_dim, bias=False),
                nn.SiLU(),
                nn.Linear(inter_dim, hidden_dim, bias=False)
            ) for _ in range(num_routed_experts)
        ])
        
        self.router = nn.Linear(hidden_dim, num_routed_experts, bias=False)

    def forward(self, x: torch.Tensor):
        B, S, D = x.shape
        x_flat = x.view(-1, D)
        
        # 1. Compute Shared Experts
        shared_out = torch.zeros_like(x_flat)
        for exp in self.shared_experts:
            shared_out += exp(x_flat)
            
        # 2. Compute Routed Experts
        logits = self.router(x_flat)
        scores = F.softmax(logits, dim=-1)
        
        topk_weights, topk_indices = torch.topk(scores, self.top_k, dim=-1)
        
        # Normalize topk weights
        topk_weights = topk_weights / topk_weights.sum(dim=-1, keepdim=True)
        
        routed_out = torch.zeros_like(x_flat)
        
        # Vectorized dispatch would be used in CUDA. 
        # For Torch/Python zero-mock, we iterate experts.
        for i, expert in enumerate(self.routed_experts):
            # Find tokens routed to this expert
            mask = (topk_indices == i)
            token_indices = mask.any(dim=-1).nonzero(as_tuple=True)[0]
            
            if len(token_indices) > 0:
                expert_in = x_flat[token_indices]
                expert_out = expert(expert_in)
                
                # Extract the specific weight for this expert for these tokens
                # Extract weight where topk_indices == i
                weight_mask = mask[token_indices]
                w = topk_weights[token_indices][weight_mask].unsqueeze(-1)
                
                routed_out.index_add_(0, token_indices, expert_out * w)
                
        # 3. Combine
        final_out = shared_out + routed_out
        return final_out.view(B, S, D)
