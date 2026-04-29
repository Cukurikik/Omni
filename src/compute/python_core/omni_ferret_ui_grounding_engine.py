"""OmniFerretUIGroundingEngine.

Handles point-and-box sub-region referential mapping
for Apple's Ferret-UI multimodal architecture.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniFerretUIGroundingEngine:
    """Zero-mock engine for Ferret-UI referential point mapping."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniFerretUIGroundingEngine",
            "version": "1.0.0",
            "primitive": "sub_region_referential_mapper",
            "monadic_enforcement": True,
        }

    @staticmethod
    def validate_point_in_box(point: List[float], box: List[float]) -> Result:
        """
        Validates if a tapped coordinate (point) correctly falls within
        the predicted visual bounding box of an element.
        point: [x, y], box: [x1, y1, x2, y2]
        """
        if len(point) != 2:
            return Err(ValueError("Point must be [x, y]"))
        if len(box) != 4:
            return Err(ValueError("Box must be [x1, y1, x2, y2]"))
            
        px, py = point
        x1, y1, x2, y2 = box
        
        # Normalize if box coords are reversed
        nx1, nx2 = min(x1, x2), max(x1, x2)
        ny1, ny2 = min(y1, y2), max(y1, y2)
        
        is_inside = (nx1 <= px <= nx2) and (ny1 <= py <= ny2)
        
        return Ok({
            "is_inside": is_inside,
            "point": point,
            "normalized_box": [nx1, ny1, nx2, ny2]
        })
