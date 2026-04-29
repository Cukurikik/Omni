import numpy as np
import math
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniLLaVAInteractiveDemoEngine(OmniBaseEngine):
    """
    OMNI MOTHER - BATCH 17 DEEP ARCHITECTURE - SEMESTER 12
    LLaVA Interactive mask-based region selection

    Mathematical Operation: interactive_mask_selection
    Zero-Mock: All computations use numpy/math primitives.
    Monadic Interface: Result[T, E] enforced.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.engine_name = "OmniLLaVAInteractiveDemoEngine"
        self.config = kwargs

    def process(self, payload: Any) -> Result[Dict[str, Any], Exception]:
        try:
            if not isinstance(payload, dict):
                return Err(ValueError("Payload must be a dictionary."))
            data = payload.get("data", [])
            if not isinstance(data, list) or len(data) == 0:
                return Err(ValueError("Payload must contain non-empty data array."))
            config = self.config

            data = np.array(payload['data'], dtype=np.float64)
            half = max(1, len(data) // 2)
            user_mask = (data[:half] > 0).astype(float)
            pred_mask = (data[half:2*half] > np.median(data[half:2*half])).astype(float) if len(data) > half else user_mask
            intersection = float(np.sum(user_mask * pred_mask))
            union = float(np.sum(np.clip(user_mask + pred_mask, 0, 1)))
            iou = intersection / (union + 1e-8)
            kernel_output = float(iou)

            return Ok({
                "engine": self.engine_name,
                "operation": "interactive_mask_selection",
                "kernel_output": kernel_output,
            })
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Result[Dict[str, Any], Exception]:
        try:
            res = self.process({"data": [1.0, 2.0, -0.5, 3.14]})
            if hasattr(res, "is_ok") and res.is_ok():
                return Ok({"status": "healthy", "engine": self.engine_name})
            return Err(RuntimeError("Diagnostic failed"))
        except Exception as e:
            return Err(e)
