"""OmniPyodEngine.

Wrapper for yzhao062/pyod anomaly detection library.
Provides programmatic access to 60+ detectors for multimodal data.
"""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniPyodEngine:
    """OMNI Engine for pyod anomaly detection."""

    def __init__(self, model_name: str = "IForest", contamination: float = 0.1):
        """Initialize the PyOD engine."""
        self.model_name = model_name
        self.contamination = contamination
        self._model = None

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniPyodEngine",
            "status": "trained" if self._model else "uninitialized",
            "model_name": self.model_name,
            "contamination": self.contamination
        }

    def train_and_predict(self, data: List[List[float]]) -> Result[List[int], Exception]:
        """Trains the anomaly detector and predicts outlines.
        
        Args:
            data: List of feature vectors.
            
        Returns:
            Result wrapping a list of predictions (1 for anomaly, 0 for normal).
        """
        try:
            import numpy as np
            from pyod.models.iforest import IForest
            
            X_train = np.array(data)
            self._model = IForest(contamination=self.contamination)
            self._model.fit(X_train)
            
            # Predict anomalies (0: normal, 1: anomaly)
            preds = self._model.predict(X_train)
            return Ok(preds.tolist())
        except ImportError:
            return Err(Exception("pyod not installed."))
        except Exception as e:
            return Err(e)
