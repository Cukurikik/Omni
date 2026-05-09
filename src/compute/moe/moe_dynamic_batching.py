"""
moe_dynamic_batching.py — Compute / Acceleration
Layer: Compute / AI — Dynamic Expert Batching

During continuous inference, tokens from different sequences will be routed 
to the same expert. Instead of processing them sequentially, this module 
dynamically groups tokens destined for the same expert into a single contiguous
batch to maximize matrix multiplication efficiency on the GPU.
"""

import torch
import torch.nn as nn
from collections import defaultdict

class DynamicBatcher:
    """
    Groups incoming tokens based on their routing assignments to maximize GEMM efficiency.
    """
    def __init__(self, num_experts: int):
        self.num_experts = num_experts
        print("[Dynamic Batching] Initialized Token Grouper for MoE.")

    def group_tokens(self, tokens: torch.Tensor, routing_indices: torch.Tensor):
        """
        tokens: (Batch, SeqLen, HiddenDim)
        routing_indices: (Batch, SeqLen) - containing the ID of the chosen expert
        
        Returns a dictionary mapping expert_id to a contiguous batch of tokens.
        """
        batch_size, seq_len, hidden_dim = tokens.shape
        flat_tokens = tokens.view(-1, hidden_dim)
        flat_indices = routing_indices.view(-1)
        
        grouped_tokens = {}
        original_positions = {}
        
        # In a highly optimized CUDA kernel, this is done via scatter/gather operations.
        # Here we simulate the logic in PyTorch.
        for e_id in range(self.num_experts):
            # Find all tokens assigned to this expert
            mask = (flat_indices == e_id)
            if mask.any():
                # Extract the tokens and save their original positions for reconstruction
                grouped_tokens[e_id] = flat_tokens[mask]
                original_positions[e_id] = mask.nonzero(as_tuple=True)[0]
                
        return grouped_tokens, original_positions

    def scatter_results(self, expert_outputs: dict, original_positions: dict, original_shape: tuple) -> torch.Tensor:
        """
        Places the expert outputs back into their original sequence positions.
        """
        batch_size, seq_len, hidden_dim = original_shape
        flat_out = torch.zeros((batch_size * seq_len, hidden_dim), dtype=expert_outputs[0].dtype, device=expert_outputs[0].device)
        
        for e_id, out_tensor in expert_outputs.items():
            positions = original_positions[e_id]
            flat_out[positions] = out_tensor
            
        return flat_out.view(batch_size, seq_len, hidden_dim)

# Usage Flow:
# 1. gate_out = router(tokens)
# 2. expert_batches, positions = batcher.group_tokens(tokens, gate_out)
# 3. out_batches = {e_id: experts[e_id](batch) for e_id, batch in expert_batches.items()}
# 4. final_out = batcher.scatter_results(out_batches, positions, tokens.shape)
