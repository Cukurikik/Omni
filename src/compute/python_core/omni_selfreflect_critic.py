from typing import List

class OmniSelfReflectCritic:
    """OMNI Compute Layer: Self-Reflection Critic (Zero-Mock)"""
    
    def __init__(self, threshold: float):
        self.threshold = threshold

    def critique_trajectory(self, trajectory: List[str]) -> bool:
        if not trajectory:
            return False
            
        score = 0.0
        for step in trajectory:
            if "error" not in step.lower() and "fail" not in step.lower():
                score += 1.0
                
        avg_score = score / len(trajectory)
        return avg_score >= self.threshold
