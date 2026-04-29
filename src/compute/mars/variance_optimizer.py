from typing import Any
import numpy as np

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class MARSOptimizer:
    def __init__(self, lr: float = 0.001):
        self.lr = lr

    def step_with_variance_reduction(self, grads: np.ndarray, prev_grads: np.ndarray) -> OmniResult:
        if grads is None or prev_grads is None:
            return OmniResult(None, "Null gradients")
            
        try:
            # MARS Variance reduction mathematical formulation
            reduced_grad = grads + 0.1 * (grads - prev_grads)
            update = -self.lr * reduced_grad
            return OmniResult(update)
        except Exception as e:
            return OmniResult(None, str(e))
