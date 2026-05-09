"""
moe_mlx_apple_silicon.py — System / Apple Silicon
Layer: Compute / Acceleration — MLX (Apple Silicon) MoE Implementation

Inspired by `andresnowak/Mixture-of-Experts-mlx`.
PyTorch is heavily optimized for Nvidia CUDA. To run the OMNI MoE locally on 
MacBooks (M1/M2/M3), we must implement the expert routing and computation natively
using Apple's MLX framework, which utilizes the Unified Memory Architecture (UMA).
"""

import mlx.core as mx
import mlx.nn as nn

class MlxExpert(nn.Module):
    def __init__(self, hidden_dim: int):
        super().__init__()
        # SwiGLU activation block
        self.w1 = nn.Linear(hidden_dim, hidden_dim * 4, bias=False)
        self.w2 = nn.Linear(hidden_dim, hidden_dim * 4, bias=False)
        self.w3 = nn.Linear(hidden_dim * 4, hidden_dim, bias=False)

    def __call__(self, x: mx.array) -> mx.array:
        # SwiGLU = (x * w1) * sigmoid(x * w1) * (x * w2)
        act = self.w1(x) * mx.sigmoid(self.w1(x))
        return self.w3(act * self.w2(x))

class MlxMoELayer(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        
        self.gate = nn.Linear(hidden_dim, num_experts, bias=False)
        self.experts = [MlxExpert(hidden_dim) for _ in range(num_experts)]
        print(f"[MLX] Initialized MLX MoE Layer for Apple Silicon. {num_experts} Experts, Top-{top_k} routing.")

    def __call__(self, x: mx.array) -> mx.array:
        # x shape: (batch, seq_len, hidden_dim)
        original_shape = x.shape
        x_flat = x.reshape(-1, original_shape[-1])
        
        # 1. Routing
        logits = self.gate(x_flat)
        # Get top-k indices and values (MLX arrays)
        top_k_indices = mx.argpartition(-logits, self.top_k, axis=-1)[:, :self.top_k]
        
        # We need to gather the logits corresponding to top_k_indices
        # MLX indexing for gather operations
        row_indices = mx.arange(x_flat.shape[0])[:, None]
        top_k_logits = logits[row_indices, top_k_indices]
        
        # Softmax over the top-k to get routing weights
        routing_weights = mx.softmax(top_k_logits, axis=-1)
        
        # 2. Expert Execution
        # Initialize output array of zeros
        final_output = mx.zeros_like(x_flat)
        
        # MLX is optimized for JIT compilation, so iterating over experts is fine
        for i, expert in enumerate(self.experts):
            # Find tokens routed to this expert
            expert_mask = (top_k_indices == i)
            
            # If any tokens are assigned to this expert
            if mx.any(expert_mask):
                # We do a naive implementation here for simplicity.
                # In highly optimized MLX, we'd use scatter/gather or indexing
                expert_output = expert(x_flat)
                
                # Multiply by weight and add to final output where mask is true
                for k in range(self.top_k):
                    mask_k = (top_k_indices[:, k] == i)
                    weights_k = routing_weights[:, k:k+1]
                    final_output = mx.where(
                        mask_k[:, None], 
                        final_output + (expert_output * weights_k), 
                        final_output
                    )
                    
        return final_output.reshape(original_shape)
