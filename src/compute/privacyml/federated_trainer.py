import numpy as np
from typing import Dict, Any, List

class OmniResult:
    def __init__(self, data: Any = None, error: str = None):
        self.data = data
        self.error = error

class FederatedTrainer:
    def __init__(self, model_dim: int):
        self.model_dim = model_dim
        # Global model weights
        self.global_weights = np.zeros(model_dim)

    def aggregate_gradients(self, encrypted_gradients: List[np.ndarray]) -> OmniResult:
        try:
            if not encrypted_gradients:
                return OmniResult(error="No gradients provided for aggregation.")
            
            for grad in encrypted_gradients:
                if grad.shape != (self.model_dim,):
                    return OmniResult(error="Gradient dimension mismatch.")

            # Mathematical aggregation (FedAvg approximation over encrypted domain logic)
            aggregated = np.mean(encrypted_gradients, axis=0)
            
            # Update global weights
            learning_rate = 0.01
            self.global_weights -= learning_rate * aggregated
            
            return OmniResult(data={"status": "aggregated", "norm": float(np.linalg.norm(self.global_weights))})
        except Exception as e:
            return OmniResult(error=f"Aggregation failed: {str(e)}")

    def add_laplace_noise(self, tensor: np.ndarray, epsilon: float = 1.0) -> OmniResult:
        try:
            if epsilon <= 0:
                return OmniResult(error="Epsilon must be strictly positive.")
                
            # Differential Privacy: Add Laplace noise
            b = 1.0 / epsilon
            noise = np.random.laplace(0, b, size=tensor.shape)
            noised_tensor = tensor + noise
            
            return OmniResult(data=noised_tensor)
        except Exception as e:
            return OmniResult(error=f"Noise addition failed: {str(e)}")
