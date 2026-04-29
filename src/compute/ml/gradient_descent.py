import numpy as np
from typing import Tuple

class OmniOptimizerError(Exception):
    pass

def compute_gradient_descent(
    X: np.ndarray, y: np.ndarray, learning_rate: float, epochs: int
) -> Tuple[np.ndarray, float]:
    if X.shape[0] != y.shape[0]:
        raise OmniOptimizerError("Dimension mismatch between X and y")
        
    m, n = X.shape
    weights = np.zeros(n)
    
    for _ in range(epochs):
        predictions = X.dot(weights)
        errors = predictions - y
        gradient = (2/m) * X.T.dot(errors)
        weights -= learning_rate * gradient
        
    final_predictions = X.dot(weights)
    mse = float(np.mean((final_predictions - y) ** 2))
    return weights, mse
