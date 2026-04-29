import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class UncertaintyOComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[UncertaintyOComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class UncertaintyOEngine:
    """
    OMNI Engine: Uncertainty-o
    Calculates epistemic and aleatoric uncertainty bounds for language generation outputs based on mathematical matrix norms.
    """
    def __init__(self, beta: float = 0.05, max_length: int = 16384):
        self.beta = beta
        self.max_length = max_length

    def calculate_epistemic_variance(self, logit_matrix: np.ndarray) -> Result:
        try:
            if not isinstance(logit_matrix, np.ndarray):
                return Result(None, UncertaintyOComputeError("Input must be a valid np.ndarray"))
            if len(logit_matrix.shape) != 2:
                return Result(None, UncertaintyOComputeError("Logit matrix must be 2-dimensional (Tokens x Vocab)"))
            if logit_matrix.shape[0] > self.max_length:
                return Result(None, UncertaintyOComputeError(f"Token length {logit_matrix.shape[0]} exceeds constraint {self.max_length}"))
                
            # Deterministic calculation of Variance across logits
            softmax_probs = np.exp(logit_matrix) / np.sum(np.exp(logit_matrix), axis=1, keepdims=True)
            entropy = -np.sum(softmax_probs * np.log(softmax_probs + 1e-12), axis=1)
            mean_entropy = float(np.mean(entropy))
            epistemic_var = mean_entropy * self.beta
            
            return Result({'epistemic_variance': epistemic_var, 'mean_entropy': mean_entropy, 'stable': True})
        except Exception as e:
            return Result(None, UncertaintyOComputeError(f"Calculation failed deterministically: {str(e)}"))

    def validate_confidence_intervals(self, entropy_val: float) -> Result:
        try:
            if entropy_val < 0:
                return Result(None, UncertaintyOComputeError("Entropy cannot be mathematically negative"))
            if entropy_val > math.log(50257): # Assuming GPT-2 vocab limit size max
                return Result(None, UncertaintyOComputeError("Entropy exceeds maximum theoretical boundary limit"))
            
            # Confidence geometric bound
            conf_interval = 1.0 / (1.0 + math.exp(entropy_val - self.beta))
            bounds = (conf_interval - 0.01, conf_interval + 0.01)
            
            return Result({'confidence': conf_interval, 'lower_bound': bounds[0], 'upper_bound': bounds[1]})
        except Exception as e:
            return Result(None, UncertaintyOComputeError(f"Validation fault: {str(e)}"))
