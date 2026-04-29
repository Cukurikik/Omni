import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class AktivaAIComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[AktivaAIComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class AktivaAIEngine:
    """
    OMNI Engine: AktivaAI
    Processes geometric vector transformations for financial active portfolio state estimations inside agentic workflows.
    """
    def __init__(self, learning_rate: float = 0.01, risk_free_rate: float = 0.02):
        self.learning_rate = learning_rate
        self.risk_free_rate = risk_free_rate

    def calculate_sharpe_tensor(self, returns_tensor: np.ndarray, covariance_matrix: np.ndarray) -> Result:
        try:
            if not isinstance(returns_tensor, np.ndarray) or not isinstance(covariance_matrix, np.ndarray):
                return Result(None, AktivaAIComputeError("Inputs must be np.ndarrays"))
            
            if returns_tensor.shape[0] != covariance_matrix.shape[0]:
                return Result(None, AktivaAIComputeError("Dimensionality mismatch between returns and covariance matrix"))
                
            port_return = float(np.sum(returns_tensor))
            port_volatility = math.sqrt(float(np.dot(returns_tensor.T, np.dot(covariance_matrix, returns_tensor))))
            
            if port_volatility <= 0:
                return Result(None, AktivaAIComputeError("Volatility cannot be zero or negative mathematically"))
                
            sharpe_ratio = (port_return - self.risk_free_rate) / port_volatility
            
            is_optimal = bool(sharpe_ratio > 1.5)
            
            return Result({'sharpe_ratio': sharpe_ratio, 'portfolio_return': port_return, 'volatility': port_volatility, 'is_optimal': is_optimal})
        except Exception as e:
            return Result(None, AktivaAIComputeError(f"Tensor calculation failed: {str(e)}"))

    def compute_gradient_penalty(self, weight_vector: np.ndarray) -> Result:
        try:
            if float(np.sum(weight_vector)) <= 0.99 or float(np.sum(weight_vector)) >= 1.01:
                return Result(None, AktivaAIComputeError("Weights must mathematically sum to 1.0"))
                
            penalty = float(np.sum(weight_vector ** 2) * self.learning_rate)
            return Result({'gradient_penalty': penalty})
        except Exception as e:
            return Result(None, AktivaAIComputeError(f"Penalty calculation failed: {str(e)}"))
