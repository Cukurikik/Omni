# OMNI Compute Layer - Megatron Tensor Parallel
import numpy as np

class MegatronError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def partition_linear_layer_column(weight: np.ndarray, world_size: int, rank: int) -> Result:
    """Column-wise Tensor Parallel partition for Megatron-LM."""
    try:
        if weight.shape[1] % world_size != 0:
            return Result(error=MegatronError("Matrix width not divisible by world size"))
            
        partition_size = weight.shape[1] // world_size
        start_idx = rank * partition_size
        end_idx = start_idx + partition_size
        
        sharded_weight = weight[:, start_idx:end_idx]
        
        return Result(value={"sharded_weight": sharded_weight, "partition_size": partition_size})
    except Exception as e:
        return Result(error=MegatronError(f"Partitioning failed: {str(e)}"))
