# Omni FM-AD Autonomous Driving Scenario Engine
# Ref: TUM-AVS/FM-AD-Survey — Apache-2.0
import math
from typing import List, Dict, Tuple

def generate_trajectory(start: Tuple[float,float], end: Tuple[float,float], n_points: int = 20) -> List[Tuple[float,float]]:
    return [(start[0] + (end[0]-start[0])*t/(n_points-1),
             start[1] + (end[1]-start[1])*t/(n_points-1)) for t in range(n_points)]

def collision_check(traj_a: List[Tuple[float,float]], traj_b: List[Tuple[float,float]], threshold: float = 2.0) -> Dict:
    for i, (a, b) in enumerate(zip(traj_a, traj_b)):
        dist = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
        if dist < threshold:
            return {"collision": True, "timestep": i, "distance": round(dist, 4)}
    return {"collision": False, "min_distance": round(min(math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2) for a,b in zip(traj_a,traj_b)), 4)}

def scenario_criticality(velocities: List[float], distances: List[float]) -> float:
    ttc_values = [d / max(v, 0.01) for d, v in zip(distances, velocities)]
    min_ttc = min(ttc_values) if ttc_values else float('inf')
    return round(1.0 / (1.0 + min_ttc), 4)

def classify_scenario(features: Dict) -> str:
    if features.get("pedestrian", False): return "pedestrian_crossing"
    if features.get("intersection", False): return "intersection_conflict"
    if features.get("highway", False): return "highway_merge"
    return "normal_driving"
