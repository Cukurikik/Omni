"""
omni_mixtral_moe.py — Sparse Mixture of Experts (Top-K)
Layer: Compute / AI
Inspired by: mistralai/mixtral-8x7b

Implements a Sparse Mixture of Experts (MoE) routing layer, typical of Mixtral.
Each token is routed to the Top-K (usually 2) experts out of N. Zero mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniExpert(nn.Module):
    def __init__(self, d_model: int, hidden_dim: int):
        super().__init__()
        # Using a standard two-layer FFN with GELU for the expert
        self.w1 = nn.Linear(d_model, hidden_dim, bias=False)
        self.w2 = nn.Linear(hidden_dim, d_model, bias=False)
        self.act = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w2(self.act(self.w1(x)))

class OmniSparseMoE(nn.Module):
    def __init__(self, d_model: int, hidden_dim: int, num_experts: int = 8, top_k: int = 2):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        
        # Router: projects token embeddings to expert logits
        self.router = nn.Linear(d_model, num_experts, bias=False)
        
        # Experts
        self.experts = nn.ModuleList([OmniExpert(d_model, hidden_dim) for _ in range(num_experts)])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, SeqLen, D_model)
        """
        batch_size, seq_len, d_model = x.shape
        flat_x = x.view(-1, d_model) # (Batch * SeqLen, D_model)
        
        # 1. Routing
        router_logits = self.router(flat_x) # (Batch * SeqLen, NumExperts)
        routing_weights = F.softmax(router_logits, dim=1) # (Batch * SeqLen, NumExperts)
        
        # 2. Select Top-K Experts
        # routing_weights_topk: (Batch * SeqLen, TopK)
        # selected_experts: (Batch * SeqLen, TopK)
        routing_weights_topk, selected_experts = torch.topk(routing_weights, self.top_k, dim=1)
        
        # Re-normalize the routing weights for the selected experts
        routing_weights_topk = routing_weights_topk / routing_weights_topk.sum(dim=-1, keepdim=True)
        
        # 3. Dispatch and compute
        final_output = torch.zeros_like(flat_x) # (Batch * SeqLen, D_model)
        
        # We iterate over experts. In highly optimized CUDA (like Megablocks), this is done
        # via block-sparse matrix multiplication without a Python loop.
        for expert_idx in range(self.num_experts):
            # Find tokens assigned to this expert
            # mask: (Batch * SeqLen, TopK) boolean
            expert_mask = (selected_experts == expert_idx)
            
            # token_idx: which tokens in the flattened batch go to this expert
            # k_idx: which routing "slot" (0 to TopK-1) triggered this assignment
            token_idx, k_idx = torch.where(expert_mask)
            
            if token_idx.numel() > 0:
                # Extract tokens for this expert
                expert_input = flat_x[token_idx]
                
                # Pass through expert
                expert_output = self.experts[expert_idx](expert_input)
                
                # Multiply by routing weight
                # routing_weight: (NumAssignedTokens,)
                weight = routing_weights_topk[token_idx, k_idx].unsqueeze(1)
                
                # Add to final output
                final_output[token_idx] += expert_output * weight

        return final_output.view(batch_size, seq_len, d_model)
