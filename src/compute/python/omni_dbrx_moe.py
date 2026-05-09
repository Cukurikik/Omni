import torch
import torch.nn as nn
import torch.nn.functional as F

# OMNI MOTHER: DBRX Fine-Grained MoE Implementation
# DBRX uses 16 experts and selects 4 (Top-4 routing). 
# This requires high-performance token dropping and capacity management.

class OmniDBRXMoE(nn.Module):
    def __init__(self, hidden_dim: int, ffn_dim: int, num_experts: int = 16, top_k: int = 4):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_experts = num_experts
        self.top_k = top_k
        
        self.router = nn.Linear(hidden_dim, num_experts, bias=False)
        
        # DBRX uses GLU-based MLP
        self.w1 = nn.Parameter(torch.randn(num_experts, hidden_dim, ffn_dim * 2)) # For GLU
        self.w2 = nn.Parameter(torch.randn(num_experts, ffn_dim, hidden_dim))

    def forward(self, x: torch.Tensor):
        B, S, D = x.shape
        x_flat = x.view(-1, D)
        
        logits = self.router(x_flat)
        scores = F.softmax(logits, dim=-1)
        
        topk_weights, topk_indices = torch.topk(scores, self.top_k, dim=-1)
        topk_weights = topk_weights / topk_weights.sum(dim=-1, keepdim=True) # Normalize
        
        out_flat = torch.zeros_like(x_flat)
        
        # In a real Triton kernel, we use batched matrix multiplications with dynamic shapes.
        # For this zero-mock inference graph, we loop through experts.
        for e in range(self.num_experts):
            # Mask of tokens routed to expert `e`
            mask = (topk_indices == e)
            if not mask.any():
                continue
                
            token_idx = mask.any(dim=-1).nonzero(as_tuple=True)[0]
            tokens = x_flat[token_idx]
            
            # SwiGLU forward pass
            # w1_e: [D, FFN * 2]
            w1_e = self.w1[e]
            w2_e = self.w2[e]
            
            h = tokens @ w1_e
            # Split into gate and up
            gate, up = h.chunk(2, dim=-1)
            h_out = F.silu(gate) * up
            
            expert_out = h_out @ w2_e
            
            # Weight application
            # topk_weights: [N, K], mask: [N, K]
            w_idx = mask[token_idx]
            w = topk_weights[token_idx][w_idx].unsqueeze(-1)
            
            out_flat.index_add_(0, token_idx, expert_out * w)
            
        return out_flat.view(B, S, D)
