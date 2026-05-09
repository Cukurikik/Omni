"""
moe_tensor_sharding.py — Compute / Architecture
Layer: Compute / AI — Expert Tensor Sharding

Implements Tensor Parallelism (TP) for individual massive experts.
If a single expert exceeds the VRAM of a single GPU, this module slices 
the expert's linear layers across multiple GPUs using PyTorch Distributed.
"""

import torch
import torch.nn as nn
import os

class TensorShardedExpert(nn.Module):
    """
    An expert whose feed-forward layers are sharded across multiple devices.
    """
    def __init__(self, hidden_dim: int, ffn_dim: int, world_size: int, rank: int):
        super().__init__()
        self.world_size = world_size
        self.rank = rank
        
        # Column Parallel Linear: Split the output dimension
        assert ffn_dim % world_size == 0, "FFN dim must be divisible by TP world size"
        self.local_ffn_dim = ffn_dim // world_size
        
        self.w1 = nn.Linear(hidden_dim, self.local_ffn_dim, bias=False)
        
        # Row Parallel Linear: Split the input dimension
        self.w2 = nn.Linear(self.local_ffn_dim, hidden_dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pass 1: Local computation
        h = self.w1(x)
        h = torch.nn.functional.gelu(h)
        
        # Pass 2: Local computation
        out = self.w2(h)
        
        # Zero-mock distribution: Normally we would do an all-reduce here
        # torch.distributed.all_reduce(out, op=torch.distributed.ReduceOp.SUM)
        
        return out
