import numpy as np
from typing import List

class BlaGPTTree:
    def compute_gini(self, class_probabilities: List[float]) -> float:
        if not class_probabilities:
            return 0.0
        probs = np.array(class_probabilities)
        return float(1.0 - np.sum(probs**2))
