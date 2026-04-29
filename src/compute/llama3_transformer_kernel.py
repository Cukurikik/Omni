from typing import Optional, List, Tuple
import numpy as np

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self):
        if self.error:
            raise Exception(self.error)
        return self.value

def compute_attention_scores(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> Result:
    try:
        scores = np.matmul(q, k.transpose(-2, -1)) / np.sqrt(q.shape[-1])
        attention = np.exp(scores) / np.sum(np.exp(scores), axis=-1, keepdims=True)
        out = np.matmul(attention, v)
        return Result(value=out)
    except Exception as e:
        return Result(error=f"Attention computation failed: {str(e)}")
