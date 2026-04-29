import numpy as np
from typing import Tuple, List, Optional

# OMNI NEURALFORECAST: N-BEATS Core Algorithm
# Pure NumPy implementation of the N-BEATS block for interpretable time-series forecasting.
# Source: Nixtla/neuralforecast

class NBeatsBlockError(Exception):
    pass

class NBeatsBlock:
    def __init__(self, 
                 input_size: int, 
                 theta_size: int, 
                 basis_function: str, 
                 num_layers: int = 4, 
                 layer_width: int = 256):
        self.input_size = input_size
        self.theta_size = theta_size
        self.basis_function = basis_function
        
        # Initialize dense MLPs (He initialization)
        self.weights = []
        self.biases = []
        
        curr_in = input_size
        for _ in range(num_layers):
            w = np.random.randn(curr_in, layer_width) * np.sqrt(2. / curr_in)
            b = np.zeros(layer_width)
            self.weights.append(w)
            self.biases.append(b)
            curr_in = layer_width
            
        # Final projection layer to theta
        self.theta_w = np.random.randn(layer_width, theta_size) * np.sqrt(2. / layer_width)
        self.theta_b = np.zeros(theta_size)

    def forward(self, x: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[NBeatsBlockError]]:
        """
        Forward pass. Returns (backcast, forecast, error).
        Monadic error handling via Tuple.
        """
        try:
            if x.shape[-1] != self.input_size:
                return None, None, NBeatsBlockError(f"Expected input size {self.input_size}, got {x.shape[-1]}")
                
            h = x
            # FC Layers with ReLU
            for w, b in zip(self.weights, self.biases):
                h = np.dot(h, w) + b
                h = np.maximum(0, h) # ReLU
                
            # Projection
            theta = np.dot(h, self.theta_w) + self.theta_b
            
            # Basis decomposition
            backcast, forecast = self._apply_basis(theta)
            return backcast, forecast, None
            
        except Exception as e:
            return None, None, NBeatsBlockError(str(e))

    def _apply_basis(self, theta: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Applies trend or seasonality basis functions.
        """
        # For simplicity in this pure implementation, we use a generic polynomial trend basis
        t_b = np.linspace(0, 1, self.input_size)
        t_f = np.linspace(1, 2, self.theta_size) # Out of sample
        
        # Power matrix: [t^0, t^1, t^2, ...]
        T_b = np.power(t_b.reshape(-1, 1), np.arange(self.theta_size))
        T_f = np.power(t_f.reshape(-1, 1), np.arange(self.theta_size))
        
        backcast = np.dot(theta, T_b.T)
        forecast = np.dot(theta, T_f.T)
        
        return backcast, forecast

# Stacking mechanism
class NBeatsStack:
    def __init__(self, blocks: List[NBeatsBlock]):
        self.blocks = blocks
        
    def forecast(self, x: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[NBeatsBlockError]]:
        residuals = x.copy()
        total_forecast = 0
        
        for block in self.blocks:
            backcast, forecast, err = block.forward(residuals)
            if err: return None, err
            
            residuals = residuals - backcast
            total_forecast = total_forecast + forecast
            
        return total_forecast, None
