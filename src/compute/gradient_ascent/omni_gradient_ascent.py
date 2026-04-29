from typing import Dict, Any, List, Callable
from dataclasses import dataclass
import numpy as np

# OMNI Gradient Ascent Optimizer Engine
# Computational Layer
# Zero-mock numerical optimizer for feature maximization

@dataclass
class AscentResult:
    ok: bool
    optimized_input: np.ndarray = None
    final_activation: float = 0.0
    error: str = None

class OmniGradientAscentEngine:
    def __init__(self, step_size: float = 0.05, max_iterations: int = 100):
        self.step_size = step_size
        self.max_iterations = max_iterations
        self.optimizations = 0

    def optimize_mathematically(self, initial_input: np.ndarray, obj_func: Callable[[np.ndarray], float], grad_func: Callable[[np.ndarray], np.ndarray]) -> AscentResult:
        """
        Executes raw numerical gradient ascent to maximize `obj_func`.
        Strictly relies on the supplied analytical gradient function to avoid PyTorch/TF dependency in this module.
        (obj_func and grad_func are computationally decoupled injections from System Layer FFI)
        """
        if not isinstance(initial_input, np.ndarray):
            return AscentResult(False, error="AscentError: Expected numpy array starting point.")
            
        self.optimizations += 1
        
        current_input = initial_input.copy()
        try:
            for i in range(self.max_iterations):
                # Request analytical gradient for current point
                gradient = grad_func(current_input)
                
                # Math limits: avoid gradient explosion
                grad_norm = np.linalg.norm(gradient)
                if grad_norm > 1e-8:
                    normalized_grad = gradient / grad_norm
                else:
                    normalized_grad = gradient
                    
                # Ascent step
                current_input = current_input + (self.step_size * normalized_grad)
                
            # After loop finishes, get the final objective score
            final_score = obj_func(current_input)
            
            return AscentResult(True, optimized_input=current_input, final_activation=float(final_score))
            
        except Exception as e:
            return AscentResult(False, error=f"AscentError: Gradient traversal failure: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniGradientAscentEngine",
            "step_size": self.step_size,
            "max_iterations": self.max_iterations,
            "optimizations_ran": self.optimizations,
            "status": "Operational"
        }
