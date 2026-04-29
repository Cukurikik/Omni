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
class OmniRitcvInfraEngine:
    """
    OmniRitcvInfraEngine
    Domain: RITCV (Robot Interaction & Teleoperation Computer Vision)
    Provides a zero-mock perspective projection mathematical core.
    Translates 3D spatial points into 2D camera intrinsic pixel coordinates
    to align robotic actuators with visual reasoning agents.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def _perspective_projection(self, points_3d: np.ndarray, focal_length: float, cx: float, cy: float) -> np.ndarray:
        """
        Calculates 3D to 2D perspective projection scaling using pinhole camera math.
        points_3d: (N, 3) 
        Returns points_2d: (N, 2)
        """
        # Ensure points are strictly in front of the camera to avoid divide-by-zero
        z_safe = np.maximum(points_3d[:, 2], 1e-6)
        
        # Pinhole projection
        x_proj = (points_3d[:, 0] * focal_length) / z_safe + cx
        y_proj = (points_3d[:, 1] * focal_length) / z_safe + cy
        
        points_2d = np.stack((x_proj, y_proj), axis=-1)
        return points_2d

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "spatial_points" not in payload:
                return err("Missing 3D spatial_points array in payload.")
            if "camera_intrinsics" not in payload:
                return err("Missing camera_intrinsics parameters.")

            pts = np.array(payload["spatial_points"], dtype=np.float32)
            intrinsics = payload["camera_intrinsics"]
            
            f = float(intrinsics.get("focal_length", 800.0))
            cx = float(intrinsics.get("cx", 320.0))
            cy = float(intrinsics.get("cy", 240.0))

            if pts.ndim != 2 or pts.shape[1] != 3:
                return err("Spatial points must be 2D array of shape (N, 3)")
                
            projected_2d = self._perspective_projection(pts, f, cx, cy)

            return ok({
                "engine_id": self.engine_id,
                "projected_2d_pixels": projected_2d.tolist(),
                "status": "RITCV Perspective Alignment Completed"
            })
            
        except Exception as e:
            return err(f"RITCV Infra perspective projection failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniRitcvInfraEngine",
            "status": "Operational"
        }
