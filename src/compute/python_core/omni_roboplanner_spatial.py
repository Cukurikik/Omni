# Omni RoboPlanner Spatial Engine
from typing import Tuple, List, Dict
import math

def calculate_kinematic_distance(pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
    """Calculate 3D Euclidean distance for robotic planning."""
    return math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 + (pos1[2]-pos2[2])**2)

def validate_trajectory_collision(trajectory: List[Tuple[float, float, float]], obstacles: List[Tuple[float, float, float]], safe_radius: float = 0.5) -> bool:
    """Check if a robotic trajectory collides with known obstacles."""
    for point in trajectory:
        for obs in obstacles:
            if calculate_kinematic_distance(point, obs) < safe_radius:
                return False # Collision detected
    return True # Safe

def score_trajectory_efficiency(trajectory: List[Tuple[float, float, float]]) -> float:
    """Calculate the total path length of a trajectory."""
    if len(trajectory) < 2:
        return 0.0
    length = sum(calculate_kinematic_distance(trajectory[i], trajectory[i-1]) for i in range(1, len(trajectory)))
    return round(length, 4)
