"""OmniCogAgentGUIEngine.

Calculates exact layout spatial grounding metrics for
CogAgent high-resolution GUI understanding.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniCogAgentGUIEngine:
    """Production mathematical engine for CogAgent GUI bounding boxes."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniCogAgentGUIEngine",
            "version": "1.0.0",
            "primitive": "gui_spatial_grounding",
            "monadic_enforcement": True,
        }

    @staticmethod
    def compute_iou(box1: List[float], box2: List[float]) -> Result:
        """
        Computes Intersection over Union (IoU) for GUI bounding box
        grounding validation. Boxes are [x1, y1, x2, y2].
        """
        if len(box1) != 4 or len(box2) != 4:
            return Err(ValueError("Boxes must have 4 coordinates [x1, y1, x2, y2]"))
            
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])
        
        if x_right < x_left or y_bottom < y_top:
            return Ok({"iou": 0.0, "intersection_area": 0.0})
            
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union_area = float(box1_area + box2_area - intersection_area)
        
        if union_area == 0:
            return Ok({"iou": 0.0, "intersection_area": 0.0})
            
        iou = intersection_area / union_area
        
        return Ok({
            "iou": iou,
            "intersection_area": intersection_area,
            "union_area": union_area
        })
