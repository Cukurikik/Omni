import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class MEXAComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[MEXAComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class MEXAEngine:
    """
    OMNI Engine: MEXA 
    Multi-Expert Alignment Mathematical framework for routing expert LLM outputs based on entropy logic.
    """
    def __init__(self, ensemble_temperature: float = 0.5):
        self.ensemble_temperature = ensemble_temperature

    def compute_expert_entropy(self, expert_logits: np.ndarray) -> Result:
        try:
            if len(expert_logits.shape) != 1:
                return Result(None, MEXAComputeError("Logits tensor structurally invalid, requires [Vocab] 1D format"))
                
            # Softmax
            exp_logits = np.exp((expert_logits - np.max(expert_logits)) / max(0.01, self.ensemble_temperature))
            probs = exp_logits / np.sum(exp_logits)
            
            # Shannon Entropy
            entropy = -float(np.sum(probs * np.log(probs + 1e-12)))
            
            return Result({'entropy': entropy, 'confidence_score': 1.0 / (1.0 + entropy)})
        except Exception as e:
            return Result(None, MEXAComputeError(f"Expert metric failed: {str(e)}"))

    def aggregate_ensemble_consensus(self, expert_scores: np.ndarray, expert_weights: np.ndarray) -> Result:
        try:
            if expert_scores.shape != expert_weights.shape:
                return Result(None, MEXAComputeError("Expert tensor weights physically misaligned"))
                
            weight_sum = np.sum(expert_weights)
            if weight_sum <= 0.0:
                return Result(None, MEXAComputeError("Weight normalization degenerate: Zero sum mass"))
                
            normalized_weights = expert_weights / weight_sum
            consensus = float(np.dot(expert_scores, normalized_weights))
            
            return Result({'consensus_value': consensus, 'active_experts': int(np.sum(expert_weights > 0))})
        except Exception as e:
            return Result(None, MEXAComputeError(f"Consensus aggregation logic error: {str(e)}"))
