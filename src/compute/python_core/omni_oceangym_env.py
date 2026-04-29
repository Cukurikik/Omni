from typing import Tuple

class OmniOceanGymEnv:
    """OMNI Compute Layer: OceanGym Underwater Agent Environment"""
    
    def __init__(self, depth_limit: float = 1000.0):
        self.depth_limit = depth_limit

    def step(self, action: List[float], current_depth: float) -> Tuple[float, float, bool]:
        if not action:
            return current_depth, 0.0, False
            
        # Deterministic physics mock for underwater AUV
        vertical_thrust = action[0]
        new_depth = current_depth + vertical_thrust
        
        if new_depth > self.depth_limit:
            new_depth = self.depth_limit
            
        reward = -0.1 if new_depth >= self.depth_limit else 1.0
        done = new_depth >= self.depth_limit or new_depth <= 0
        
        return float(new_depth), float(reward), bool(done)
