from typing import List

class OmniBYOXML:
    """OMNI Compute Layer: Build-Your-Own-X ML Engine (Zero-Mock)"""
    
    def __init__(self, learning_rate: float, epochs: int):
        self.lr = learning_rate
        self.epochs = epochs

    def train_linear_regression(self, x: List[float], y: List[float]) -> tuple[float, float]:
        if len(x) != len(y) or len(x) == 0:
            raise ValueError("Mismatched or empty data arrays")
            
        m, c = 0.0, 0.0
        n = len(x)
        
        for _ in range(self.epochs):
            dm, dc = 0.0, 0.0
            for i in range(n):
                y_pred = m * x[i] + c
                error = y_pred - y[i]
                dm += x[i] * error
                dc += error
                
            m -= self.lr * (2.0/n) * dm
            c -= self.lr * (2.0/n) * dc
            
        return m, c
