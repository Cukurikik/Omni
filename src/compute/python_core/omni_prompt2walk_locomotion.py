# Omni Prompt2Walk Locomotion Controller
# Ref: HybridRobotics/prompt2walk
import math
from typing import Dict, List
def generate_gait_params(command: str) -> Dict:
    c = command.lower()
    speed = 1.0 if "fast" in c else 0.3 if "slow" in c else 0.6
    stride = speed * 0.4
    return {"speed": speed, "stride_length": round(stride, 4), "frequency": round(speed * 2.5, 4)}
def compute_reward(target_vel: float, actual_vel: float, energy: float, w_vel: float = 1.0, w_energy: float = 0.01) -> float:
    return round(w_vel * math.exp(-abs(target_vel - actual_vel)) - w_energy * energy, 6)
