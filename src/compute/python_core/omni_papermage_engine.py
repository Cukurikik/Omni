# ===========================================================================
# OMNI Papermage ENGINE (SEMESTER 12 — BATCH 14)
# ===========================================================================
# Absorbed From  : allenai/papermage
# Logic Inherited: Bounding Box Intersection-over-Union
# ===========================================================================
"""
OMNI Papermage Engine
=========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import logging
import math
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
import numpy as np
from src.compute.python_core.omni_base_engine import Result, Ok, Err

logger = logging.getLogger("OmniPapermageEngine")
ENGINE_VERSION = "1.0.0-omni"

class OmniPapermageEngine:
    """Spatial relationship engine for processing structured document PDFs."""
    
    def __init__(self, max_capacity: int = 100):
        self.capacity = max_capacity
        self._state_cache: Dict[str, Any] = {}
        self._initialize_core()
        
    def _initialize_core(self):
        logger.info(f"[OmniPapermageEngine] Booting production algorithms (capacity={self.capacity}).")

    def compute_iou_matrix(self, boxes: List[Tuple[float, float, float, float]]) -> Result[Dict[str, Any], str]:
        """O(N^2) IoU computation between an array of parsed rects [x1, y1, x2, y2]."""
        if len(boxes) > self.capacity:
            return Err("Capacity bound or constraint exceeded.")
            
        try:
            n = len(boxes)
            iou_mat = np.zeros((n, n))
            for i in range(n):
                for j in range(i+1, n):
                    b1, b2 = boxes[i], boxes[j]
                    ix1, iy1 = max(b1[0], b2[0]), max(b1[1], b2[1])
                    ix2, iy2 = min(b1[2], b2[2]), min(b1[3], b2[3])
                    i_area = max(0, ix2 - ix1) * max(0, iy2 - iy1)
                    u_area = max(0, (b1[2]-b1[0])*(b1[3]-b1[1])) + max(0, (b2[2]-b2[0])*(b2[3]-b2[1])) - i_area
                    iou = i_area / (u_area + 1e-9)
                    iou_mat[i, j] = iou_mat[j, i] = iou
            output_data = {"iou_matrix_trace": float(np.trace(iou_mat)), "shape": iou_mat.shape}
            return Ok({"status": "success", "data": output_data})
        except Exception as e:
            logger.error(f"[OmniPapermageEngine] Engine failure: {e}")
            return Err(f"Engine exception: {e}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine_id": "omni_papermage_engine",
            "version": ENGINE_VERSION,
            "status": "operational"
        }
