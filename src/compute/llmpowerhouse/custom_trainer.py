from typing import Any
import numpy as np

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class CustomTrainer:
    def __init__(self, learning_rate: float = 3e-4):
        self.lr = learning_rate

    def custom_step(self, loss_gradient: np.ndarray) -> OmniResult:
        if loss_gradient is None or loss_gradient.size == 0:
            return OmniResult(None, "Invalid gradient")
            
        try:
            weight_update = -self.lr * loss_gradient
            return OmniResult(weight_update)
        except Exception as e:
            return OmniResult(None, str(e))
