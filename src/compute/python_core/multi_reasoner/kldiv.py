import numpy as np

class ReasonerKLDivergence:
    def compute_kl(self, p: np.ndarray, q: np.ndarray) -> float:
        if len(p) != len(q) or len(p) == 0:
            raise ValueError("Invalid distribution arrays")
        # Ensure non-zero
        p = np.clip(p, 1e-10, 1.0)
        q = np.clip(q, 1e-10, 1.0)
        p = p / np.sum(p)
        q = q / np.sum(q)
        return float(np.sum(p * np.log(p / q)))
