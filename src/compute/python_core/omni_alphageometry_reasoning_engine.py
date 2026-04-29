import uuid
from typing import Dict, Any, List
from dataclasses import dataclass, field
import numpy as np

# OMNI Monadic Type
@dataclass
class Result:
    is_ok: bool
    value: Any = None
    error: str = None

    @classmethod
    def Ok(cls, value: Any):
        return cls(is_ok=True, value=value)

    @classmethod
    def Err(cls, error: str):
        return cls(is_ok=False, error=error)

def ok(value: Any) -> Result:
    return Result.Ok(value)

def err(error: str) -> Result:
    return Result.Err(error)

@dataclass
class OmniAlphageometryReasoningEngine:
    """
    OmniAlphageometryReasoningEngine
    Domain: AlphaGeometry (Neuro-symbolic Euclidean Geometry)
    Acts as the numeric proxy for symbolic point deduction. Calculates exact geometric
    angle convergence from coordinates to evaluate theorem bounds (e.g. collinearity, perpendicularity).
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    epsilon_geometric: float = 1e-4

    def _angle_between_points(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> np.ndarray:
        """
        Calculates angle at P2 given P1, P2, P3 using vector dot products.
        """
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Norms
        norm_v1 = np.linalg.norm(v1, axis=-1, keepdims=True)
        norm_v2 = np.linalg.norm(v2, axis=-1, keepdims=True)
        
        # Prevent division by zero
        safe_div = np.maximum(norm_v1 * norm_v2, 1e-12)
        
        dot_prod = np.sum(v1 * v2, axis=-1, keepdims=True)
        cos_theta = np.clip(dot_prod / safe_div, -1.0, 1.0)
        
        angles = np.arccos(cos_theta)
        return angles

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if not all(k in payload for k in ["point_a", "point_b", "point_c"]):
                return err("Missing geometric coordinate sequence.")
                
            pa = np.array(payload["point_a"], dtype=np.float32)
            pb = np.array(payload["point_b"], dtype=np.float32)
            pc = np.array(payload["point_c"], dtype=np.float32)

            if pa.ndim != 2 or pb.ndim != 2 or pc.ndim != 2:
                return err("Points must be 2D positional arrays (Batch, Coordinates).")

            # Assess collinearity through the angle (0 or Pi)
            angles = self._angle_between_points(pa, pb, pc)
            
            # Check deviation from Pi
            deviation_from_pi = np.abs(angles - np.pi)
            deviation_from_zero = np.abs(angles)
            
            is_collinear = np.logical_or(
                deviation_from_pi < self.epsilon_geometric,
                deviation_from_zero < self.epsilon_geometric
            )

            return ok({
                "engine_id": self.engine_id,
                "calculated_angles_rad": angles.tolist(),
                "is_collinear_theorem": is_collinear.tolist(),
                "status": "AlphaGeometry Points Evaluated"
            })
            
        except Exception as e:
            return err(f"AlphaGeometry calculation failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniAlphageometryReasoningEngine",
            "status": "Operational",
            "epsilon_constraint": self.epsilon_geometric
        }
