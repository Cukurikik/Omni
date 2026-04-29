from typing import List

class OmniReflexionActor:
    """OMNI Compute Layer: Reflexion Self-Evaluation Engine"""
    
    def __init__(self, max_reflections: int = 3):
        self.max_reflections = max_reflections

    def generate_reflection(self, previous_trajectory: str, reward: float) -> str:
        if reward >= 0.9:
            return "Trajectory successful. No reflection needed."
            
        # Deterministic heuristic reflection
        if "timeout" in previous_trajectory.lower():
            return "Reflexion: The previous action took too long. I need to use a faster heuristic next time."
        elif "error" in previous_trajectory.lower():
            return "Reflexion: The code produced a syntax error. I must check variable declarations."
            
        return "Reflexion: The output did not meet criteria. I should rethink the approach."
