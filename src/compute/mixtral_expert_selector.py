import numpy as np

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def select_experts(routing_logits: np.ndarray, top_k: int = 2) -> Result:
    try:
        top_indices = np.argsort(routing_logits, axis=-1)[..., -top_k:]
        return Result(value=top_indices)
    except Exception as e:
        return Result(error=f"Expert selection failed: {str(e)}")
