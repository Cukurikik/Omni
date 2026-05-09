import torch
import torch.nn as nn
import torch.nn.functional as F

# OMNI MOTHER: Mixtral-style sparse MoE implementation.
# Megablocks style: 8 experts, Top-2 routing.

class OmniMixtralBlock(nn.Module):
    def __init__(self, hidden_dim: int, ffn_dim: int, num_experts: int = 8, top_k: int = 2):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_experts = num_experts
        self.top_k = top_k
        
        self.gate = nn.Linear(hidden_dim, num_experts, bias=False)
        
        # Grouped parameters for batched GEMMs in real Triton/CUDA kernels
        self.w1 = nn.Parameter(torch.randn(num_experts, hidden_dim, ffn_dim))
        self.w2 = nn.Parameter(torch.randn(num_experts, ffn_dim, hidden_dim))
        self.w3 = nn.Parameter(torch.randn(num_experts, hidden_dim, ffn_dim))

    def forward(self, x: torch.Tensor):
        # x: [batch * seq_len, hidden_dim]
        orig_shape = x.shape
        x = x.view(-1, self.hidden_dim)
        
        router_logits = self.gate(x)
        routing_weights = F.softmax(router_logits, dim=1)
        
        routing_weights, selected_experts = torch.topk(routing_weights, self.top_k, dim=-1)
        routing_weights /= routing_weights.sum(dim=-1, keepdim=True)
        
        final_hidden_states = torch.zeros_like(x)
        
        # One-hot mask for dispatch
        expert_mask = torch.nn.functional.one_hot(selected_experts, num_classes=self.num_experts)
        expert_mask = expert_mask.permute(2, 1, 0) # [num_experts, top_k, num_tokens]
        
        for expert_idx in range(self.num_experts):
            idx_mask = expert_mask[expert_idx]
            token_mask = idx_mask.any(dim=0)
            
            if not token_mask.any():
                continue
                
            # Gather tokens for this expert
            current_state = x[token_mask]
            
            # Forward pass: SiLU(x @ w1) * (x @ w3) @ w2
            # w1: [hidden_dim, ffn_dim]
            h = F.silu(current_state @ self.w1[expert_idx]) * (current_state @ self.w3[expert_idx])
            expert_out = h @ self.w2[expert_idx]
            
            # Get weights
            # selected_experts: [num_tokens, top_k]
            # routing_weights: [num_tokens, top_k]
            expert_weights = (selected_experts[token_mask] == expert_idx).float()
            expert_weights = (expert_weights * routing_weights[token_mask]).sum(dim=-1, keepdim=True)
            
            current_hidden_states = expert_out * expert_weights
            final_hidden_states.index_add_(0, token_mask.nonzero().squeeze(-1), current_hidden_states)

        return final_hidden_states.view(orig_shape)
