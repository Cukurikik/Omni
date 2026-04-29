from typing import List, Tuple

class OmniInfiGUIAEPO:
    """OMNI Compute Layer: InfiGUI G1 AEPO Policy (Zero-Mock)"""
    
    def __init__(self, exploration_rate: float):
        self.epsilon = max(0.0, min(1.0, exploration_rate))

    def select_action(self, state_features: List[float], possible_actions: List[str]) -> str:
        if not possible_actions:
            raise ValueError("No actions available")
            
        # Deterministic Q-value computation
        q_values = [(action, sum(state_features) * (idx + 1)) for idx, action in enumerate(possible_actions)]
        
        # Threshold logic
        if sum(state_features) % 1.0 < self.epsilon:
            return possible_actions[0] # Explore
        
        return max(q_values, key=lambda x: x[1])[0] # Exploit
