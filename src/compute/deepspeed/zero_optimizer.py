import torch
from typing import Tuple, Optional, List

# OMNI DEEPSPEED: Zero Redundancy Optimizer (ZeRO) Core Logic
# Logic for partitioning optimizer states across data parallel ranks.
# Source: microsoft/DeepSpeed

class ZeROError(Exception):
    pass

class ZeROptimizerStage1:
    """
    Implements the logic of ZeRO Stage 1: Optimizer State Partitioning.
    Instead of every GPU holding the full Adam optimizer states (momentum, variance),
    the states are chunked and distributed across N GPUs.
    """
    def __init__(self, parameters: List[torch.Tensor], world_size: int, rank: int):
        if world_size <= 0 or rank < 0 or rank >= world_size:
            raise ValueError("Invalid world_size or rank.")
            
        self.world_size = world_size
        self.rank = rank
        
        # Flatten all parameters into a single 1D tensor
        self.flat_params = torch.cat([p.data.view(-1) for p in parameters])
        self.total_elements = self.flat_params.numel()
        
        # Calculate partition boundaries
        # We ensure equal chunk sizes by padding if necessary (omitted for pure structural simplicity here)
        self.partition_size = (self.total_elements + self.world_size - 1) // self.world_size
        
        self.start_idx = self.rank * self.partition_size
        self.end_idx = min(self.start_idx + self.partition_size, self.total_elements)
        
        # Only allocate optimizer states for THIS rank's partition
        self.partition_length = self.end_idx - self.start_idx
        
        # Adam states (fp32)
        if self.partition_length > 0:
            self.exp_avg = torch.zeros(self.partition_length, dtype=torch.float32)
            self.exp_avg_sq = torch.zeros(self.partition_length, dtype=torch.float32)
        else:
            self.exp_avg = None
            self.exp_avg_sq = None
            
        self.step = 0

    def step_partition(self, flat_gradients: torch.Tensor, lr: float = 1e-3, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8) -> Tuple[Optional[torch.Tensor], Optional[ZeROError]]:
        """
        Performs the Adam step ONLY on the partition assigned to this rank.
        Requires that the global gradients have been reduced (All-Reduce) before calling.
        """
        try:
            if self.partition_length <= 0:
                return None, None # Nothing to update on this rank
                
            self.step += 1
            
            # Extract the gradient partition for this rank
            grad_partition = flat_gradients[self.start_idx:self.end_idx]
            
            # Adam Update
            self.exp_avg.mul_(beta1).add_(grad_partition, alpha=1.0 - beta1)
            self.exp_avg_sq.mul_(beta2).addcmul_(grad_partition, grad_partition, value=1.0 - beta2)
            
            bias_correction1 = 1.0 - beta1 ** self.step
            bias_correction2 = 1.0 - beta2 ** self.step
            
            step_size = lr / bias_correction1
            denom = (self.exp_avg_sq.sqrt() / math.sqrt(bias_correction2)).add_(eps)
            
            # Compute parameter updates for this partition
            param_updates = (self.exp_avg / denom) * step_size
            
            # Apply updates directly to the flattened param view (modifies original tensors if view is maintained)
            self.flat_params[self.start_idx:self.end_idx].sub_(param_updates)
            
            return self.flat_params[self.start_idx:self.end_idx], None
            
        except Exception as e:
            import math
            return None, ZeROError(f"ZeRO Partition step failed: {str(e)}")
