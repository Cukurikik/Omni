"""
OMNI Nano-Neuron Engine
========================
Production-grade OMNI engine abstracting foundational supervised learning
constructs from trekhleb/nano-neuron.

Features:
- Miniaturized feedforward propagation (single neuron / linear constraint).
- Cost calculation (Mean Squared Error).
- Backpropagation (Gradient computation).
- Deterministic Vectorized Training Loops.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class NanoNeuronErr(Exception):
    """OMNI Zero-Prod Production Implementation for NanoNeuronErr."""
    pass


@dataclass(frozen=True)
class Ok:
    """OMNI Zero-Prod Production Implementation for Ok."""
    value: Any


@dataclass(frozen=True)
class Err:
    """OMNI Zero-Prod Production Implementation for Err."""
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. SEVEN FUNCTIONS ABSTRACTION
# ---------------------------------------------------------------------------
# Adhering to the original 7 core functionalities translated into ML arrays

class NanoNeuron:
    """Core mathematical model mapping linear equation y = w*x + b."""
    
    def __init__(self, w: float = 0.5, b: float = 0.5):
        self.w = float(w)
        self.b = float(b)

    def predict(self, x: np.ndarray) -> np.ndarray:
        """1. Forward pass (Prediction)."""
        return self.w * x + self.b

    @staticmethod
    def cost(predictions: np.ndarray, targets: np.ndarray) -> float:
        """2. Cost function (Mean Squared Error)."""
        errors = predictions - targets
        return float(np.mean(errors ** 2) / 2.0)

    def forward_and_backward(self, x: np.ndarray, targets: np.ndarray) -> Tuple[float, float, float]:
        """3 & 4. Compute cost and partial derivatives (Gradients)."""
        predictions = self.predict(x)
        cost_val = self.cost(predictions, targets)
        
        # dJ/dw = (1/N) * sum((pred - y) * x)
        # dJ/db = (1/N) * sum(pred - y)
        errors = predictions - targets
        dw = float(np.mean(errors * x))
        db = float(np.mean(errors))
        
        return cost_val, dw, db

    def train_step(self, x: np.ndarray, targets: np.ndarray, lr: float) -> float:
        """5 & 6. Update weights."""
        cost_val, dw, db = self.forward_and_backward(x, targets)
        self.w -= lr * dw
        self.b -= lr * db
        return cost_val


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniNanoNeuronEngine:
    """
    Production Engine to spawn and train lightweight Neurons.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-nano-neuron"

    def __init__(self) -> None:
        self.neurons: Dict[str, NanoNeuron] = {}

    def create_neuron(self, name: str, init_w: float = 0.5, init_b: float = 0.5) -> Result:
        """Create a new NanoNeuron instance."""
        if name in self.neurons:
            return Err(f"Neuron '{name}' already exists.")
        self.neurons[name] = NanoNeuron(init_w, init_b)
        return Ok(name)

    def train(self, name: str, x_data: List[float], y_data: List[float],
              epochs: int = 1000, learning_rate: float = 0.01) -> Result:
        """Execute full training loop over entire dataset."""
        neuron = self.neurons.get(name)
        if neuron is None:
            return Err(f"Neuron '{name}' not found.")
            
        if len(x_data) != len(y_data) or not x_data:
            return Err("Mismatched or empty training data arrays.")
            
        x_arr = np.array(x_data, dtype=np.float64)
        y_arr = np.array(y_data, dtype=np.float64)
        
        history = []
        try:
            for epoch in range(epochs):
                cost = neuron.train_step(x_arr, y_arr, learning_rate)
                # Store every 10th epoch or last to save memory
                if epoch % 10 == 0 or epoch == epochs - 1:
                    history.append(cost)
                    
            return Ok({
                "final_w": neuron.w,
                "final_b": neuron.b,
                "final_cost": history[-1] if history else cost,
                "cost_history": history
            })
        except Exception as exc:
            return Err(f"Training failed: {exc}")

    def predict(self, name: str, x_val: float) -> Result:
        """Predict output for a single value."""
        neuron = self.neurons.get(name)
        if neuron is None:
            return Err(f"Neuron '{name}' not found.")
        try:
            pred = neuron.predict(np.array([x_val]))
            return Ok(float(pred[0]))
        except Exception as exc:
            return Err(f"Prediction failed: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "active_neurons": len(self.neurons),
            "features": [
                "linear_forward_propagation",
                "mse_cost_function",
                "gradient_backpropagation",
                "gradient_descent_optimizer",
            ]
        }
