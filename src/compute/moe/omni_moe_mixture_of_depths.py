import torch
import torch.nn as nn
import torch.nn.functional as F

# OMNI MOTHER Production Zero-Mock Mixture of Depths (MoD)
# Dynamically skips computation for 'easy' tokens in the sequence length
# to save massive amounts of compute during MoE execution.

class MixtureOfDepthsRouter(nn.Module):
    def __init__(self, d_model: int, capacity_factor: float = 0.5):
        super().__init__()
        self.d_model = d_model
        self.capacity_factor = capacity_factor # Only process top X% of tokens
        self.routing_linear = nn.Linear(d_model, 1, bias=False)

    def forward(self, x: torch.Tensor):
        # x: [Batch, SeqLen, D_model]
        B, S, D = x.size()
        
        # Calculate routing scores
        scores = self.routing_linear(x).squeeze(-1) # [B, S]
        
        # We only want to process the top (capacity_factor * S) tokens
        k = max(1, int(S * self.capacity_factor))
        
        # Find Top-K indices per sequence in batch
        topk_scores, topk_indices = torch.topk(scores, k, dim=-1)
        
        # Create binary mask (1 for process, 0 for skip)
        mask = torch.zeros_like(scores, dtype=torch.bool)
        mask.scatter_(-1, topk_indices, True)
        
        return mask, scores

class ModTransformerLayer(nn.Module):
    def __init__(self, d_model: int, base_layer: nn.Module, capacity_factor: float = 0.5):
        super().__init__()
        self.router = MixtureOfDepthsRouter(d_model, capacity_factor)
        self.base_layer = base_layer # Could be MoE or standard Attention/MLP

    def forward(self, x: torch.Tensor):
        B, S, D = x.size()
        
        # 1. Routing
        mask, scores = self.router(x)
        
        # 2. Extract tokens to process
        # For simplicity in PyTorch, we can use boolean indexing. 
        # In custom CUDA, this is a memory gather operation.
        
        # Residual connection copy
        output = x.clone()
        
        # Process only active tokens
        active_tokens = x[mask] # [N_active, D]
        
        if active_tokens.numel() > 0:
            # We reshape to [1, N_active, D] to pass to standard layers if needed,
            # or the base_layer must support flattened inputs.
            processed_tokens = self.base_layer(active_tokens)
            
            # Scatter back to output
            output[mask] = output[mask] + processed_tokens
            
        return output
