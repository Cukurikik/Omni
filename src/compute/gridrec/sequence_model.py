from typing import Any
import numpy as np

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class GridSequenceModel:
    def compute_transition_probs(self, state_matrix: np.ndarray) -> OmniResult:
        if state_matrix is None or len(state_matrix.shape) != 2:
            return OmniResult(None, "Invalid state matrix for GRID")
            
        try:
            # Mathematical sequential recommendation logic
            # Row-wise softmax for transition probabilities
            exp_mat = np.exp(state_matrix - np.max(state_matrix, axis=1, keepdims=True))
            probs = exp_mat / np.sum(exp_mat, axis=1, keepdims=True)
            return OmniResult(probs)
        except Exception as e:
            return OmniResult(None, str(e))
