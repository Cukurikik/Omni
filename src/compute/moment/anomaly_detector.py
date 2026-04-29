from typing import Any
import numpy as np

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class AnomalyDetector:
    def detect_spikes(self, timeseries: np.ndarray, threshold_std: float = 3.0) -> OmniResult:
        if timeseries is None or timeseries.size == 0:
            return OmniResult(None, "Empty time series")
            
        try:
            mean = np.mean(timeseries)
            std = np.std(timeseries)
            
            anomalies = np.abs(timeseries - mean) > (threshold_std * std)
            return OmniResult(anomalies)
        except Exception as e:
            return OmniResult(None, str(e))
