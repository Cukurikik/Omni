"""
omni_tensor_sharder.py — 1D Tensor Parallelism
Layer: System / GPU
Inspired by: hpcaitech/ColossalAI

Implements 1D Tensor Parallel (Megatron-LM style) column and row linear layers.
Splits the weight matrices across multiple GPUs to reduce memory limits and
executes distributed matrix multiplications. Zero mock.
"""

import torch
import torch.nn as nn
import torch.distributed as dist
import torch.nn.functional as F

class OmniColumnParallelLinear(nn.Module):
    def __init__(self, in_features: int, out_features: int, process_group=None):
        super().__init__()
        self.process_group = process_group if process_group else dist.group.WORLD
        self.world_size = dist.get_world_size(self.process_group)
        self.rank = dist.get_rank(self.process_group)
        
        assert out_features % self.world_size == 0, "Out features must be divisible by world size"
        self.local_out_features = out_features // self.world_size
        
        # X @ W
        # We split W along the columns (output dimension)
        self.weight = nn.Parameter(torch.empty(self.local_out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(self.local_out_features))
        nn.init.kaiming_uniform_(self.weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # X is (Batch, In)
        # Local W is (LocalOut, In)
        # Result is (Batch, LocalOut)
        local_out = F.linear(x, self.weight, self.bias)
        
        # Forward pass output is partitioned. No communication needed if feeding into RowParallel next.
        return local_out

class OmniRowParallelLinear(nn.Module):
    def __init__(self, in_features: int, out_features: int, process_group=None):
        super().__init__()
        self.process_group = process_group if process_group else dist.group.WORLD
        self.world_size = dist.get_world_size(self.process_group)
        self.rank = dist.get_rank(self.process_group)
        
        assert in_features % self.world_size == 0, "In features must be divisible by world size"
        self.local_in_features = in_features // self.world_size
        
        # We split W along the rows (input dimension)
        self.weight = nn.Parameter(torch.empty(out_features, self.local_in_features))
        self.bias = nn.Parameter(torch.zeros(out_features))
        nn.init.kaiming_uniform_(self.weight)
        
        # Bias is only added by rank 0 during all-reduce to prevent multiple additions
        if self.rank != 0:
            self.bias.data.zero_()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # X is (Batch, LocalIn)
        # Local W is (Out, LocalIn)
        # Result is (Batch, Out)
        local_out = F.linear(x, self.weight)
        
        # All-Reduce across GPUs to sum the partial results
        dist.all_reduce(local_out, op=dist.ReduceOp.SUM, group=self.process_group)
        
        # Add bias (only rank 0's bias is non-zero, but all_reduce synchronized the data, 
        # so we just add the local bias everywhere)
        local_out = local_out + self.bias
        
        return local_out
