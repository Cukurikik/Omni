# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# LeeDL Tutorial Backpropagation (OMNI Zero-Mock Implementation)
# Implements exact mathematical derivation of single-layer gradient chain rule without libraries.

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class Result:
    value: Optional[Tuple[List[float], float]] # Gradients and Loss
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: Tuple[List[float], float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class LeeDLBackprop:
    def sigmoid(self, x: float) -> float:
        z = max(min(x, 100), -100) # Prevents overflow
        if z >= 0:
            return 1.0 / (1.0 + math.exp(-z))
        else:
            e = math.exp(z)
            return e / (1.0 + e)

    def train_step(self, x: List[float], y_true: float, weights: List[float], bias: float, lr: float) -> Result:
        if len(x) != len(weights):
            return Result.err("Feature and weight vectors must be the same length.")

        # Forward Pass
        z = bias
        for xi, wi in zip(x, weights):
            z += xi * wi
            
        y_pred = self.sigmoid(z)
        
        # Loss (Binary Cross Entropy)
        loss = - (y_true * math.log(y_pred + 1e-9) + (1.0 - y_true) * math.log(1.0 - y_pred + 1e-9))
        
        # Backward Pass (Derivative of Sigmoid Loss)
        # dL/dz = y_pred - y_true 
        dz = y_pred - y_true
        
        grad_weights = [0.0] * len(weights)
        for i in range(len(weights)):
            grad_weights[i] = dz * x[i]
            
        grad_bias = dz
        
        # Weight Update (Not explicitly returned applied, returning gradients instead)
        # In actual engines, optimizers apply these.
        return Result.ok((grad_weights, grad_bias))
