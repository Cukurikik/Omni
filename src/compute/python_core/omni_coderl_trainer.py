from typing import List

class OmniCodeRLTrainer:
    """OMNI Compute Layer: CodeRL Trainer Advantage Calc (Zero-Mock)"""
    
    def __init__(self, discount_factor: float):
        self.gamma = max(0.0, min(1.0, discount_factor))

    def calculate_advantages(self, rewards: List[float], values: List[float]) -> List[float]:
        if len(rewards) != len(values):
            raise ValueError("Rewards and Values must have the same length.")
            
        advantages = [0.0] * len(rewards)
        last_adv = 0.0
        
        # Generalized Advantage Estimation (GAE) simplified
        for t in reversed(range(len(rewards))):
            next_val = values[t + 1] if t + 1 < len(values) else 0.0
            delta = rewards[t] + self.gamma * next_val - values[t]
            advantages[t] = delta + self.gamma * last_adv
            last_adv = advantages[t]
            
        return advantages
