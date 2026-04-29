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
class OmniMmposeEstimatorEngine:
    """
    OmniMmposeEstimatorEngine
    Domain: mmpose (OpenMMLab Pose Estimation)
    Mathematically extracts human joint coordinates using soft-argmax operation
    on estimated volumetric or 2D heatmaps.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    beta: float = 100.0  # Temperature scaling for soft-argmax

    def _soft_argmax_2d(self, heatmaps: np.ndarray) -> np.ndarray:
        """
        heatmaps: (Batch, Num_Keypoints, Height, Width)
        Returns coordinates: (Batch, Num_Keypoints, 2)
        """
        B, K, H, W = heatmaps.shape

        # Create coordinate grids
        x_grid = np.arange(W, dtype=np.float32)
        y_grid = np.arange(H, dtype=np.float32)
        xv, yv = np.meshgrid(x_grid, y_grid, indexing='xy')  # Both are (H, W)

        # Scale heatmaps by beta
        hm = heatmaps * self.beta
        
        # Flatten HW spatially
        hm_flat = hm.reshape(B, K, -1)
        
        # Spatial Softmax
        exp_hm = np.exp(hm_flat - np.max(hm_flat, axis=-1, keepdims=True))
        probs = exp_hm / np.sum(exp_hm, axis=-1, keepdims=True)
        probs = probs.reshape(B, K, H, W)
        
        # Expectation
        expected_x = np.sum(probs * xv, axis=(2, 3))
        expected_y = np.sum(probs * yv, axis=(2, 3))
        
        # Stack to (Batch, Num_Keypoints, 2)
        coords = np.stack([expected_x, expected_y], axis=-1)
        return coords

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "heatmaps" not in payload:
                return err("Missing heatmaps tensor for pose estimation.")
                
            hm = np.array(payload["heatmaps"], dtype=np.float32)

            if hm.ndim != 4:
                return err("Heatmaps must be a 4D array: (Batch, Keypoints, Height, Width)")

            keypoint_coords = self._soft_argmax_2d(hm)

            return ok({
                "engine_id": self.engine_id,
                "keypoint_coordinates": keypoint_coords.tolist(),
                "status": "Mmpose Joints Extracted"
            })
            
        except Exception as e:
            return err(f"Mmpose estimation failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniMmposeEstimatorEngine",
            "status": "Operational",
            "soft_argmax_beta": self.beta
        }
