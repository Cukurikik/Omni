# Omni OceanGym Underwater Agent
# Ref: OceanGPT/OceanGym
import math
from typing import Dict, List, Tuple

def compute_depth_pressure(depth_m: float) -> float:
    return round(1.0 + depth_m * 0.1, 4)  # atm

def navigate_waypoint(current: Tuple[float,float,float],
                       target: Tuple[float,float,float]) -> Dict:
    dx = target[0]-current[0]; dy = target[1]-current[1]; dz = target[2]-current[2]
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    heading = math.atan2(dy, dx) * 180 / math.pi
    return {"distance": round(dist, 4), "heading_deg": round(heading, 2),
            "depth_change": round(dz, 2)}

def energy_cost(distance: float, current_speed: float = 0.5) -> float:
    return round(distance * current_speed * 0.1, 4)
