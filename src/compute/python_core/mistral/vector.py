import numpy as np

class MistralVectorOps:
    def compute_dot_product(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        if len(vec_a) != len(vec_b) or len(vec_a) == 0:
            raise ValueError("Mismatched or empty dimensions")
        return float(np.dot(vec_a, vec_b))
