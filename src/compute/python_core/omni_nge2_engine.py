"""OmniNGE2Engine - Orthographic projection matrix computation for 3D volumetric rendering."""
import math
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniNGE2Engine:
    """OMNI Production Engine: OmniNGE2Engine. Zero-Prod compliant."""
    def __init__(self):
        self.version = "3.7.0"
        
    def compute_orthographic_matrix(self, spatial_boundaries):
        """Perform compute orthographic matrix computation.

            Args:
                    spatial_boundaries

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not isinstance(spatial_boundaries, dict):
            return {"status": "error", "error": "Invalid topological input. Expected mapping dict for left, right, bottom, top, near, far."}
            
        required_keys = ["left", "right", "bottom", "top", "near", "far"]
        if not all(k in spatial_boundaries for k in required_keys):
            return {"status": "error", "error": "Missing rigorous bounds for orthographic volume calculation."}
            
        b = spatial_boundaries
        
        if b["right"] == b["left"] or b["top"] == b["bottom"] or b["far"] == b["near"]:
            return {"status": "error", "error": "Degenerate volumetric boundary limits detected (division by zero trap)."}
        
        # Calculate exactly based on standard orthogonal metrics
        rml = b["right"] - b["left"]
        rpl = b["right"] + b["left"]
        tmb = b["top"] - b["bottom"]
        tpb = b["top"] + b["bottom"]
        fmn = b["far"] - b["near"]
        fpn = b["far"] + b["near"]
        
        ortho_matrix = [
            [2.0 / rml, 0.0, 0.0, -(rpl / rml)],
            [0.0, 2.0 / tmb, 0.0, -(tpb / tmb)],
            [0.0, 0.0, -2.0 / fmn, -(fpn / fmn)],
            [0.0, 0.0, 0.0, 1.0]
        ]
        
        # Round the values strictly
        ortho_matrix = [[round(val, 6) for val in row] for row in ortho_matrix]
        
        return {
            "status": "ok",
            "value": {
                "orthographic_projection": ortho_matrix,
                "volumetric_volume": round(rml * tmb * fmn, 4)
            }
        }
        
    def diagnostics(self):
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "version": self.version
        }
