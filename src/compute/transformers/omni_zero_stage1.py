"""
omni_zero_stage1.py — ZeRO Stage 1 Optimizer Sharding
Layer: Compute / Systems
Inspired by: microsoft/DeepSpeed

Implements the memory-sharding logic of ZeRO-1 (Zero Redundancy Optimizer).
Instead of replicating optimizer states (Adam moments) across all GPUs, 
Stage 1 partitions the optimizer state, reducing VRAM footprint drastically.
Zero mock.
"""

import torch
import torch.distributed as dist
from typing import Iterator

class OmniZeROStage1Optimizer:
    def __init__(self, optimizer: torch.optim.Optimizer, process_group=None):
        self.base_optimizer = optimizer
        self.process_group = process_group if process_group is not None else dist.group.WORLD
        
        if not dist.is_initialized():
            raise RuntimeError("OmniZeRO requires torch.distributed to be initialized.")
            
        self.world_size = dist.get_world_size(self.process_group)
        self.rank = dist.get_rank(self.process_group)
        
        self._partition_parameters()

    def _partition_parameters(self):
        """
        Assigns ownership of parameter optimizer states to specific ranks.
        """
        self.param_to_rank = {}
        for group in self.base_optimizer.param_groups:
            for i, p in enumerate(group['params']):
                # Simple round-robin assignment for ZeRO-1
                owner_rank = i % self.world_size
                self.param_to_rank[p] = owner_rank
                
                # If I don't own this parameter, clear its optimizer state locally
                if owner_rank != self.rank:
                    self.base_optimizer.state[p].clear()

    def step(self, closure=None):
        """
        Performs a distributed optimization step.
        """
        # 1. Reduce-Scatter Gradients (In a real system, hooks do this during backward)
        # Here we manually simulate the synchronization of gradients for owned parameters.
        for group in self.base_optimizer.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                
                # All ranks sum their gradients for p
                dist.all_reduce(p.grad, op=dist.ReduceOp.SUM, group=self.process_group)
                p.grad.div_(self.world_size)

        # 2. Step the optimizer only for parameters this rank owns
        # We temporarily detach gradients of non-owned parameters to prevent the base optimizer from updating them
        detached_grads = {}
        for group in self.base_optimizer.param_groups:
            for p in group['params']:
                if self.param_to_rank[p] != self.rank and p.grad is not None:
                    detached_grads[p] = p.grad
                    p.grad = None # Hide from base optimizer
        
        # Update owned parameters
        loss = self.base_optimizer.step(closure)
        
        # Restore gradients
        for p, grad in detached_grads.items():
            p.grad = grad

        # 3. Broadcast updated parameters from owners to all other ranks
        for group in self.base_optimizer.param_groups:
            for p in group['params']:
                owner = self.param_to_rank[p]
                dist.broadcast(p.data, src=owner, group=self.process_group)
                
        return loss

    def zero_grad(self, set_to_none: bool = True):
        self.base_optimizer.zero_grad(set_to_none=set_to_none)
