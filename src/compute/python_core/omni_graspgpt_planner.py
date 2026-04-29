from typing import Tuple, List

class OmniGraspGPTPlanner:
    """OMNI Compute Layer: GraspGPT Planner (Zero-Mock)"""
    
    def __init__(self, workspace_limits: Tuple[float, float, float]):
        self.limits = workspace_limits

    def calculate_grasp_pose(self, object_center: Tuple[float, float, float], normals: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
        if not normals:
            raise ValueError("Normals list cannot be empty.")
            
        # Deterministic approach vector alignment
        avg_normal_x = sum(n[0] for n in normals) / len(normals)
        avg_normal_y = sum(n[1] for n in normals) / len(normals)
        avg_normal_z = sum(n[2] for n in normals) / len(normals)
        
        approach_vector = (-avg_normal_x, -avg_normal_y, -avg_normal_z)
        
        target_pose = (
            object_center[0] + approach_vector[0] * 0.05,
            object_center[1] + approach_vector[1] * 0.05,
            object_center[2] + approach_vector[2] * 0.05
        )
        
        return target_pose
