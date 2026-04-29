import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class BioMimeticComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[BioMimeticComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class BioMimeticAgentEngine:
    """
    OMNI Engine: bio-mimetic-search
    Calculates swarm particle intelligence limits and pheromone decay gradients.
    """
    def __init__(self, pheromone_evaporation_rate: float = 0.05):
        self.evaporation_rate = pheromone_evaporation_rate

    def calculate_swarm_velocity_update(self, current_velocity: np.ndarray, global_best: np.ndarray, personal_best: np.ndarray, position: np.ndarray) -> Result:
        try:
            if not (current_velocity.shape == global_best.shape == personal_best.shape == position.shape):
                return Result(None, BioMimeticComputeError("Spatial dimensions for swarm particles do not strictly match"))
                
            w = 0.5  # Inertia weight
            c1 = 1.5 # Cognitive constant
            c2 = 1.5 # Social constant
            
            r1 = np.random.rand(*position.shape)
            r2 = np.random.rand(*position.shape)
            
            new_velocity = (w * current_velocity) + (c1 * r1 * (personal_best - position)) + (c2 * r2 * (global_best - position))
            
            # Clip velocity to prevent swarm explosion metric
            speed = np.linalg.norm(new_velocity)
            if speed > 10.0:
                 new_velocity = new_velocity * (10.0 / speed)
                 
            return Result({'updated_velocity': new_velocity})
        except Exception as e:
            return Result(None, BioMimeticComputeError(f"Swarm logic failed: {str(e)}"))

    def compute_pheromone_gradient_decay(self, current_pheromone_matrix: np.ndarray, delta_pheromone: np.ndarray) -> Result:
         try:
              if current_pheromone_matrix.shape != delta_pheromone.shape:
                   return Result(None, BioMimeticComputeError("Pheromone topologies misaligned geometrically"))
                   
              updated_map = (1.0 - self.evaporation_rate) * current_pheromone_matrix + delta_pheromone
              
              return Result({'updated_pheromone_map': updated_map})
         except Exception as e:
              return Result(None, BioMimeticComputeError(f"Pheromone bounds fault: {str(e)}"))
