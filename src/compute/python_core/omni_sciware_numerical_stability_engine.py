"""
OmniSciwareNumericalStabilityEngine (Level-2 Abstraction)
Assimilated from: flatironinstitute/sciware
Domain: Mathematical Tensor Stability & Gradient Validation
"""

from typing import Dict, Any, List, Optional

from dataclasses import dataclass
import math
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniSciwareNumericalStabilityEngine:
    """
    Evaluates raw 1D gradients/tensors for mathematical irregularities (NaN, Infinity, Underflow)
    ensuring computational stability across High Performance Computing interfaces.
    """
    
    @staticmethod
    def validate_tensor_stability(tensor: List[float], epsilon: float = 1e-9) -> Result:
        """Perform validate tensor stability computation.

            Args:
                    tensor: List[float]
                    epsilon: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not tensor:
            return Err("FATAL: Tensor payload cannot be empty.")
            
        underflow_count = 0
        peak_magnitude = 0.0
        
        for idx, val in enumerate(tensor):
            if math.isnan(val):
                return Err(f"STABILITY FAILURE: NaN detected at index {idx}.")
            if math.isinf(val):
                return Err(f"STABILITY FAILURE: Infinity detected at index {idx}.")
                
            abs_val = abs(val)
            if 0.0 < abs_val < epsilon:
                underflow_count += 1
                
            if abs_val > peak_magnitude:
                peak_magnitude = abs_val
                
        if peak_magnitude > 1e12:
            return Err(f"STABILITY WARNING: Gradient explosion imminent. Peak magnitude {peak_magnitude} exceeds safety thresholds.")
            
        return Ok({
            "tensor_size": len(tensor),
            "underflow_count": underflow_count,
            "peak_magnitude": peak_magnitude,
            "status": "STABLE"
        })

    @staticmethod
    def diagnostics() -> Dict[str, Any]:
        return {
            "engine": "OmniSciwareNumericalStabilityEngine",
            "status": "operational",
            "monadic_enforcement": True
        }
