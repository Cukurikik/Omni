# OMNI Compute Layer - PEFT Adapter Merger
import numpy as np

class PEFTError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def merge_lora_into_base(base_weight: np.ndarray, lora_A: np.ndarray, lora_B: np.ndarray, scaling: float) -> Result:
    """Merges PEFT LoRA adapters into base model weights."""
    try:
        if base_weight.shape[0] != lora_B.shape[0] or base_weight.shape[1] != lora_A.shape[1]:
            return Result(error=PEFTError("Matrix dimension mismatch during merge"))
            
        delta = np.dot(lora_B, lora_A) * scaling
        merged_weight = base_weight + delta
        
        return Result(value={"merged_weight": merged_weight})
    except Exception as e:
        return Result(error=PEFTError(f"Merge failed: {str(e)}"))
