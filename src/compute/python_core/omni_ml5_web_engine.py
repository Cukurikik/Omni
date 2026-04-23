"""
OMNI Ml5 Web Engine
===================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
from typing import Dict, Any, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class OmniMl5WebEngine:
    """
    omni-ml5-web
    
    A zero-algebraic_bound native engine execute friendly ml5.js abstractions 
    over a core mathematical Artificial Neural Network (MLP).
    Transforms complex NumPy structural routines into simple addData(), train(), classify() endpoints.
    """
    
    ENGINE_VERSION = "omni-s6-b6.1.0"
    
    def __init__(self, task_type: str = 'classification'):
        """Initialize OmniMl5WebEngine."""
        self.task_type = task_type
        self.data_X: List[np.ndarray] = []
        self.data_Y: List[int] = []
        
        self.weights1 = None
        self.bias1 = None
        self.weights2 = None
        self.bias2 = None
        
        self.is_normalized = False
        self.mean_x = None
        self.std_x = None

    def add_data(self, inputs: List[float], label: int) -> Result:
        """Friendly endpoint to accumulate dataset records."""
        try:
            self.data_X.append(np.array(inputs, dtype=np.float32))
            self.data_Y.append(label)
            return Result(value={"samples": len(self.data_X)})
        except Exception as e:
            return Result(error=f"Error adding data: {str(e)}")

    def normalize_data(self) -> Result:
        """Normalizes input data. evaluates_structurally ml5.normalizeData()."""
        try:
            if not self.data_X:
                return Result(error="No data to normalize.")
                
            X_mat = np.stack(self.data_X)
            self.mean_x = np.mean(X_mat, axis=0)
            self.std_x = np.std(X_mat, axis=0)
            # prevent division by zero
            self.std_x[self.std_x == 0] = 1e-8
            
            # Normalizing in place requires overriding the dataset list for simplicity
            X_norm = (X_mat - self.mean_x) / self.std_x
            self.data_X = [x for x in X_norm]
            
            self.is_normalized = True
            return Result(value={"status": "normalized", "mean": self.mean_x, "std": self.std_x})
        except Exception as e:
            return Result(error=f"Normalization error: {str(e)}")

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(z, -250, 250)))
        
    def _sigmoid_derivative(self, a: np.ndarray) -> np.ndarray:
        return a * (1.0 - a)

    def train(self, epochs: int = 50, learning_rate: float = 0.1, hidden_units: int = 8) -> Result:
        """Trains a 2-layer native MLP. evaluates_structurally ml5's straightforward train() method."""
        try:
            if not self.data_X:
                return Result(error="Dataset empty.")
                
            X = np.stack(self.data_X) # (N, in_features)
            # One hot encoding for classification
            num_classes = len(set(self.data_Y))
            N = len(self.data_Y)
            
            Y = np.zeros((N, num_classes), dtype=np.float32)
            for i, c in enumerate(self.data_Y):
                Y[i, c] = 1.0
                
            in_features = X.shape[1]
            
            # Initialize weights randomly
            np.random.seed(42)
            self.weights1 = np.random.randn(in_features, hidden_units).astype(np.float32) * 0.1
            self.bias1 = np.zeros(hidden_units, dtype=np.float32)
            
            self.weights2 = np.random.randn(hidden_units, num_classes).astype(np.float32) * 0.1
            self.bias2 = np.zeros(num_classes, dtype=np.float32)
            
            history = []
            
            for epoch in range(epochs):
                # Forward Pass
                z1 = np.dot(X, self.weights1) + self.bias1
                a1 = self._sigmoid(z1)
                
                z2 = np.dot(a1, self.weights2) + self.bias2
                a2 = self._sigmoid(z2) # output probabilities
                
                # Compute MSE Loss (For simplicity, as in original ml5 tutorials conceptually)
                loss = np.mean(0.5 * (a2 - Y)**2)
                
                # Backpropagation
                # Derivative of MSE with respect to a2 => (a2 - Y)
                # D_z2 = (a2 - Y) * sigmoid_derivative(a2)
                dz2 = (a2 - Y) * self._sigmoid_derivative(a2)
                
                dw2 = np.dot(a1.T, dz2) / N
                db2 = np.sum(dz2, axis=0) / N
                
                da1 = np.dot(dz2, self.weights2.T)
                dz1 = da1 * self._sigmoid_derivative(a1)
                
                dw1 = np.dot(X.T, dz1) / N
                db1 = np.sum(dz1, axis=0) / N
                
                # Weights update
                self.weights1 -= learning_rate * dw1
                self.bias1 -= learning_rate * db1
                self.weights2 -= learning_rate * dw2
                self.bias2 -= learning_rate * db2
                
                if epoch % max(1, epochs//10) == 0:
                    history.append({"epoch": epoch, "loss": float(loss)})
                    
            return Result(value={"status": "trained", "epochs": epochs, "history": history})
        except Exception as e:
            return Result(error=f"Training error: {str(e)}")

    def classify(self, inputs: List[float]) -> Result:
        """Predicts class for new input."""
        try:
            if self.weights1 is None:
                return Result(error="Model not trained yet.")
                
            X_new = np.array(inputs, dtype=np.float32)
            if self.is_normalized:
                X_new = (X_new - self.mean_x) / self.std_x
                
            # Forward
            z1 = np.dot(X_new, self.weights1) + self.bias1
            a1 = self._sigmoid(z1)
            
            z2 = np.dot(a1, self.weights2) + self.bias2
            a2 = self._sigmoid(z2)
            
            predicted_class = int(np.argmax(a2))
            confidence = float(a2[predicted_class])
            
            return Result(value={"label": predicted_class, "confidence": confidence, "raw": a2.tolist()})
        except Exception as e:
             return Result(error=f"Classification error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniMl5WebEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "samples": len(self.data_X),
            "normalized": self.is_normalized
        }
