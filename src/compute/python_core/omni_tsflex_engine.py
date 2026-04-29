import numpy as np
import math
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniTsflexEngine(OmniBaseEngine):
    """
    OMNI MOTHER - BATCH 17 DEEP ARCHITECTURE - SEMESTER 12
    Flexible time series feature extraction with sliding windows

    Mathematical Operation: sliding_window_features
    Zero-Mock: All computations use numpy/math primitives.
    Monadic Interface: Result[T, E] enforced.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.engine_name = "OmniTsflexEngine"
        self.config = kwargs

    def process(self, payload: Any) -> Result[Dict[str, Any], Exception]:
        try:
            if not isinstance(payload, dict):
                return Err(ValueError("Payload must be a dictionary."))
            data = payload.get("data", [])
            if not isinstance(data, list) or len(data) == 0:
                return Err(ValueError("Payload must contain non-empty data array."))
            config = self.config

            window_size = config.get('window_size', 3)
            stride = config.get('stride', 1)
            data = np.array(payload['data'], dtype=np.float64)
            features = []
            for i in range(0, len(data) - window_size + 1, stride):
                window = data[i:i+window_size]
                features.append([float(np.mean(window)), float(np.std(window)),
                                float(np.max(window)), float(np.min(window))])
            features = np.array(features) if features else np.zeros((1, 4))
            kernel_output = float(np.mean(features[:, 0]))

            return Ok({
                "engine": self.engine_name,
                "operation": "sliding_window_features",
                "kernel_output": kernel_output,
            })
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Result[Dict[str, Any], Exception]:
        try:
            res = self.process({"data": [1.0, 2.0, -0.5, 3.14]})
            if hasattr(res, "is_ok") and res.is_ok():
                return Ok({"status": "healthy", "engine": self.engine_name})
            return Err(RuntimeError("Diagnostic failed"))
        except Exception as e:
            return Err(e)
