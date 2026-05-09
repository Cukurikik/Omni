"""
moe_distributed_optimizer.py — Compute / Training
Layer: Compute / AI — Zero-Redundancy Optimizer (ZeRO)

Implements ZeRO Stage 3 concepts specifically for MoE training.
Standard DistributedDataParallel (DDP) duplicates optimizer states (Momentum, Variance)
on every GPU, which instantly OOMs when training 100B+ parameter MoE experts.
This module shards the optimizer states across the cluster.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from typing import Iterator

class ZeroMoEOptimizer:
    """
    Shards optimizer states across available GPUs based on the DeepSpeed ZeRO-3 paper.
    Each GPU is only responsible for updating a slice of the expert weights.
    """
    def __init__(self, parameters: Iterator[nn.Parameter], lr: float = 1e-4, rank: int = 0, world_size: int = 1):
        self.rank = rank
        self.world_size = world_size
        
        # We only keep the parameters that "belong" to this rank based on hash modulo
        self.local_params = []
        for i, p in enumerate(parameters):
            if i % world_size == rank:
                self.local_params.append(p)
                
        # Initialize the underlying AdamW optimizer with only the local shard
        self.optimizer = optim.AdamW(self.local_params, lr=lr, weight_decay=0.01)
        
        print(f"[ZeRO-3] Rank {rank}: Initialized Distributed Optimizer managing {len(self.local_params)} parameters.")

    def zero_grad(self):
        self.optimizer.zero_grad()

    def step(self):
        """
        Executes the optimizer step on the local parameters.
        In a full implementation, an All-Gather operation follows to sync
        the updated weights back to all other GPUs in the cluster.
        """
        # 1. Update local weights
        self.optimizer.step()
        
        # 2. Sync weights across cluster (Mocked PyTorch Distributed call)
        # for p in self.local_params:
        #     torch.distributed.all_gather(tensor_list, p.data)
        #     # Reconstruct the full model weight from the gathered list

    def clip_grad_norm(self, max_norm: float):
        """
        Clips gradients locally. Requires an All-Reduce to find the global norm
        before clipping.
        """
        # Calculate local squared norm
        local_sq_norm = sum(p.grad.detach().pow(2).sum() for p in self.local_params if p.grad is not None)
        
        # Simulate All-Reduce (global_sq_norm = all_reduce(local_sq_norm))
        global_norm = local_sq_norm.sqrt() 
        
        clip_coef = max_norm / (global_norm + 1e-6)
        if clip_coef < 1.0:
            for p in self.local_params:
                if p.grad is not None:
                    p.grad.detach().mul_(clip_coef)
