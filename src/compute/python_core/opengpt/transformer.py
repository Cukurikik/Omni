"""
OMNI Compute Layer - OpenGPTAndBeyond
Attention mechanism and transformer ops.
"""
import numpy as np

class OpenGPTAttention:
    def __init__(self, d_model: int):
        self.d_model = d_model
        
    def scaled_dot_product(self, q: np.ndarray, k: np.ndarray, v: np.ndarray) -> np.ndarray:
        d_k = q.shape[-1]
        scores = np.matmul(q, k.swapaxes(-2, -1)) / np.sqrt(d_k)
        # Numerically stable Softmax
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        return np.matmul(attention_weights, v)
