import numpy as np
from typing import List

class UncertaintyPlanner:
    def compute_shannon_entropy(self, probabilities: List[float]) -> float:
        probs = np.array(probabilities)
        probs = probs[probs > 0] # Avoid log(0)
        if len(probs) == 0:
            return 0.0
        return float(-np.sum(probs * np.log2(probs)))
