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
class OmniBratsTumorSegmentationEngine:
    """
    OmniBratsTumorSegmentationEngine
    Domain: BraTS (Brain Tumor Image Segmentation)
    Zero mock 3D Dice Loss mathematical evaluation. Soft dice coefficient
    for intersecting Multimodal volumetric predictions vs Ground Truth map.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    smooth: float = 1e-6

    def _soft_dice_coefficient(self, preds: np.ndarray, targets: np.ndarray) -> np.ndarray:
        """
        Calculates the Dice coefficient per channel in a 3D volumetric context.
        Expected inputs: (Channels, Depth, Height, Width)
        """
        # Element-wise multiplication for intersection
        intersection = np.sum(preds * targets, axis=(1, 2, 3))
        
        # Sum of elements
        preds_sum = np.sum(preds, axis=(1, 2, 3))
        targets_sum = np.sum(targets, axis=(1, 2, 3))
        
        dice = (2.0 * intersection + self.smooth) / (preds_sum + targets_sum + self.smooth)
        return dice

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "predicted_volumes" not in payload or "ground_truth_volumes" not in payload:
                return err("Missing 3D volume tensors for BraTS eval.")
                
            y_pred = np.array(payload["predicted_volumes"], dtype=np.float32)
            y_true = np.array(payload["ground_truth_volumes"], dtype=np.float32)

            if y_pred.ndim != 4 or y_true.ndim != 4:
                return err("Volume tensors must be 4D: (Channels, Depth, Height, Width)")
            if y_pred.shape != y_true.shape:
                return err("Prediction and ground truth volumes must match dimensions.")

            # Clip predictions explicitly for soft dice bounds
            y_pred = np.clip(y_pred, 0.0, 1.0)
            
            dice_scores = self._soft_dice_coefficient(y_pred, y_true)
            mean_dice = float(np.mean(dice_scores))

            return ok({
                "engine_id": self.engine_id,
                "class_dice_scores": dice_scores.tolist(),
                "mean_dice": mean_dice,
                "status": "BraTS 3D Volumetric Dice Extracted"
            })
            
        except Exception as e:
            return err(f"BraTS Segmentation eval failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniBratsTumorSegmentationEngine",
            "status": "Operational",
            "smoothing": self.smooth
        }
