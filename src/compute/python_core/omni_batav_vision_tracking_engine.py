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
class OmniBatavVisionTrackingEngine:
    """
    OmniBatavVisionTrackingEngine
    Domain: BATAV (Vision Tracking Alignment formulation)
    Calculates Kalman filtering update specific to visual spatial bounds
    for robust single object visual tracking against structural noise.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def _iou_tracker_update(self, predicted_box: np.ndarray, detected_box: np.ndarray, alpha: float) -> np.ndarray:
        """
        Smooths tracking predictions utilizing a linear exponential moving average (EMA/Alpha Filter)
        coupled with spatial coordinates.
        (x_min, y_min, x_max, y_max)
        """
        smoothed_box = (alpha * detected_box) + ((1.0 - alpha) * predicted_box)
        return smoothed_box

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "predicted_box" not in payload or "detected_box" not in payload:
                return err("Missing bounding box targets for tracker update.")
                
            p_box = np.array(payload["predicted_box"], dtype=np.float32)
            d_box = np.array(payload["detected_box"], dtype=np.float32)
            alpha = float(payload.get("tracking_alpha", 0.5))

            if p_box.shape != (4,) or d_box.shape != (4,):
                return err("Bounding boxes must be 1D arrays of size 4 (xmin, ymin, xmax, ymax).")

            # Check validity (xmin < xmax)
            if p_box[0] >= p_box[2] or p_box[1] >= p_box[3] or d_box[0] >= d_box[2] or d_box[1] >= d_box[3]:
                return err("Degenerate bounding box coordinates given to tracker.")

            fused_tracking_box = self._iou_tracker_update(p_box, d_box, alpha)

            return ok({
                "engine_id": self.engine_id,
                "fused_tracking_box": fused_tracking_box.tolist(),
                "status": "BATAV Tracker Position Updated"
            })
            
        except Exception as e:
            return err(f"BATAV tracking update failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniBatavVisionTrackingEngine",
            "status": "Operational"
        }
