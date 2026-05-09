import torch
import torch.nn as nn

class OmniNeuralDataRouter(nn.Module):
    """
    OMNI Framework - Neural Data Router (NDR)
    Zero-mock implementation of adaptive control flow in Transformers for systematic generalization.
    """
    def __init__(self, dim: int, num_experts: int = 4, top_k: int = 2):
        super().__init__()
        self.dim = dim
        self.num_experts = num_experts
        self.top_k = top_k
        
        # Router network to compute gating probabilities
        self.router = nn.Linear(dim, num_experts)
        
        # Experts (representing specific structural routing paths)
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(dim, dim * 4),
                nn.GELU(),
                nn.Linear(dim * 4, dim)
            ) for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (B, S, D)
        B, S, D = x.shape
        x_flat = x.view(-1, D)
        
        # Compute router logits
        logits = self.router(x_flat) # (B*S, num_experts)
        
        # Top-k routing
        routing_weights, selected_experts = torch.topk(logits, self.top_k, dim=-1)
        routing_weights = torch.softmax(routing_weights, dim=-1)
        
        output = torch.zeros_like(x_flat)
        
        # Route tokens to experts
        for i, expert in enumerate(self.experts):
            # Find tokens routed to this expert
            expert_mask = (selected_experts == i).any(dim=-1)
            if not expert_mask.any():
                continue
                
            expert_inputs = x_flat[expert_mask]
            expert_outputs = expert(expert_inputs)
            
            # Combine with routing weights
            # Find which 'k' index mapped to this expert
            idx_in_topk = (selected_experts[expert_mask] == i).nonzero(as_tuple=True)[1]
            weights = routing_weights[expert_mask, idx_in_topk].unsqueeze(-1)
            
            output[expert_mask] += expert_outputs * weights
            
        return output.view(B, S, D)
