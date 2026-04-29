from typing import List

class OmniOpenRLHFReward:
    """OMNI Compute Layer: OpenRLHF Reward Scalar (Zero-Mock)"""
    
    def __init__(self, penalty_coefficient: float):
        self.penalty = penalty_coefficient

    def compute_reward(self, base_score: float, kl_divergence: float) -> float:
        if kl_divergence < 0:
            raise ValueError("KL Divergence cannot be negative")
            
        # PPO reward with KL penalty
        return base_score - (self.penalty * kl_divergence)
