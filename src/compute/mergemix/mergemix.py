import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class MergeMixComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[MergeMixComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class MergeMixEngine:
    """
    OMNI Engine: MergeMix
    Manages geometric linear interpolation and gradient mixing for Multi-Modal LLM weight merging.
    """
    def __init__(self, slerp_tolerance: float = 0.0001):
        self.slerp_tolerance = slerp_tolerance

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(v)
        if norm == 0: 
            return v
        return v / norm

    def slerp_tensors(self, tensor_a: np.ndarray, tensor_b: np.ndarray, t: float) -> Result:
        try:
            if tensor_a.shape != tensor_b.shape:
                return Result(None, MergeMixComputeError(f"Tensor shape mismatch: {tensor_a.shape} vs {tensor_b.shape}"))
                
            if not 0.0 <= t <= 1.0:
                return Result(None, MergeMixComputeError(f"Interpolation factor {t} must be bounded [0, 1]"))
                
            a_flat = tensor_a.flatten()
            b_flat = tensor_b.flatten()
            
            a_norm = self._normalize(a_flat)
            b_norm = self._normalize(b_flat)
            
            dot_product = float(np.sum(a_norm * b_norm))
            dot_product = max(min(dot_product, 1.0), -1.0) # Floating point bounding
            
            if dot_product > 0.9995:
                # Fallback to linear interpolation (lerp)
                result_tensor = tensor_a + t * (tensor_b - tensor_a)
                return Result({'merged_tensor': result_tensor, 'method': 'lerp'})
                
            theta_0 = math.acos(dot_product)
            theta = theta_0 * t
            
            vec_slerp = b_norm - a_norm * dot_product
            vec_slerp = self._normalize(vec_slerp)
            
            res_flat = (a_norm * math.cos(theta)) + (vec_slerp * math.sin(theta))
            result_tensor = res_flat.reshape(tensor_a.shape)
            
            return Result({'merged_tensor': result_tensor, 'method': 'slerp'})
        except Exception as e:
            return Result(None, MergeMixComputeError(f"SLERP computation failed: {str(e)}"))

    def compute_gradient_divergence(self, base_grad: np.ndarray, target_grad: np.ndarray) -> Result:
        try:
            if base_grad.shape != target_grad.shape:
                return Result(None, MergeMixComputeError("Gradient shape mismatch"))
                
            div = float(np.linalg.norm(base_grad - target_grad))
            return Result({'divergence_norm': div})
        except Exception as e:
            return Result(None, MergeMixComputeError(f"Divergence calc failed: {str(e)}"))
