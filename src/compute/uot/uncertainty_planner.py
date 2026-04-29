import numpy as np
from typing import List, Dict

class UncertaintyOfThoughtsPlanner:
    def __init__(self, entropy_threshold: float = 0.5):
        self.entropy_threshold = entropy_threshold
        
    def calculate_entropy(self, probabilities: List[float]) -> float:
        p = np.array(probabilities)
        p = p[p > 0]
        return -np.sum(p * np.log(p))
        
    def plan_next_step(self, states: List[Dict]) -> str:
        # Evaluates states and seeks information if uncertainty is high
        for state in states:
            ent = self.calculate_entropy(state['probs'])
            if ent > self.entropy_threshold:
                return "SEEK_INFORMATION"
        return "ACT"
