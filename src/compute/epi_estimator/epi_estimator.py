import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class EpistemicComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[EpistemicComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class EpistemicBoundEstimatorEngine:
    """
    OMNI Engine: epistemic-bound-estimation
    Calculates aleatoric and epistemic matrices for bounding model uncertainty.
    """
    def __init__(self, confidence_interval: float = 0.95):
        self.confidence_interval = confidence_interval

    def calculate_epistemic_variance(self, ensemble_predictions: np.ndarray) -> Result:
        try:
            if len(ensemble_predictions.shape) != 2:
                return Result(None, EpistemicComputeError("Ensemble tensor requires [Experts, Predictions] structure"))
                
            num_experts = ensemble_predictions.shape[0]
            if num_experts < 2:
                 return Result(None, EpistemicComputeError("Epistemic bounds require minimum 2 topological states"))
                 
            # Mean across experts
            mean_prediction = np.mean(ensemble_predictions, axis=0)
            
            # Variance across experts (Epistemic)
            epistemic_var = np.var(ensemble_predictions, axis=0)
            average_epistemic = float(np.mean(epistemic_var))
            
            # Check if divergence destroys confidence
            is_reliable = average_epistemic < (1.0 - self.confidence_interval)
            
            return Result({'epistemic_variance_mean': average_epistemic, 'is_prediction_reliable': is_reliable})
        except Exception as e:
            return Result(None, EpistemicComputeError(f"Epistemic variance collapse: {str(e)}"))

    def compute_aleatoric_entropy(self, softmax_probs: np.ndarray) -> Result:
         try:
            if np.abs(np.sum(softmax_probs, axis=-1) - 1.0).max() > 1e-5:
                 return Result(None, EpistemicComputeError("Aleatoric bounds shattered: Probability does not sum to 1.0"))
                 
            entropy = -np.sum(softmax_probs * np.log(softmax_probs + 1e-12), axis=-1)
            mean_entropy = float(np.mean(entropy))
            
            return Result({'aleatoric_entropy': mean_entropy})
         except Exception as e:
            return Result(None, EpistemicComputeError(f"Aleatoric calculus failed: {str(e)}"))
