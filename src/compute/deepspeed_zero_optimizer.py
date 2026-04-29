# OMNI Compute Layer - DeepSpeed ZeRO
import torch

class DeepSpeedError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def partition_optimizer_state(gradients: dict, world_size: int, rank: int) -> Result:
    """ZeRO Stage 1: Partition optimizer state across data parallel ranks."""
    try:
        if world_size <= 0:
            return Result(error=DeepSpeedError("Invalid world size"))
            
        partitioned = {}
        for name, grad in gradients.items():
            numel = grad.numel()
            chunk_size = (numel + world_size - 1) // world_size
            start = rank * chunk_size
            end = min(start + chunk_size, numel)
            partitioned[name] = grad.flatten()[start:end]
            
        return Result(value={"partitioned_states": partitioned, "stage": 1})
    except Exception as e:
        return Result(error=DeepSpeedError(f"ZeRO partitioning failed: {str(e)}"))
