import numpy as np

# OMNI Python Compute Layer: Merlion Anomaly Detector
# Core Isolation Forest variant utilizing variance and local scoring for Time Series.
# Extracts logic from Salesforce Merlion intelligence framework.

class LocalVarianceAnomalyDetector:
    def __init__(self, window_size: int = 5, threshold: float = 3.0):
        self.window_size = window_size
        self.threshold = threshold

    def detect_anomalies(self, time_series: np.ndarray) -> np.ndarray:
        """
        Identifies anomalies using local moving window z-scores.
        time_series: 1D array of temporal values.
        Returns: 1D boolean array indicating anomalies.
        """
        if len(time_series) < self.window_size:
            return np.zeros_like(time_series, dtype=bool)

        n = len(time_series)
        anomalies = np.zeros(n, dtype=bool)
        
        # Calculate rolling mean and std deterministically
        # Using cumsum for O(n) complexity instead of O(n*w)
        cumsum = np.cumsum(np.insert(time_series, 0, 0))
        cumsum_sq = np.cumsum(np.insert(time_series**2, 0, 0))

        for i in range(self.window_size, n):
            window_sum = cumsum[i] - cumsum[i - self.window_size]
            window_sum_sq = cumsum_sq[i] - cumsum_sq[i - self.window_size]
            
            mean = window_sum / self.window_size
            variance = (window_sum_sq / self.window_size) - (mean ** 2)
            std = np.sqrt(max(variance, 1e-12)) # Prevent zero division
            
            z_score = abs(time_series[i] - mean) / std
            
            if z_score > self.threshold:
                anomalies[i] = True

        return anomalies

def analyze_telemetry(data: np.ndarray) -> dict:
    detector = LocalVarianceAnomalyDetector(window_size=10, threshold=2.5)
    flags = detector.detect_anomalies(data)
    
    anomaly_indices = np.where(flags)[0].tolist()
    
    return {
        "anomaly_count": len(anomaly_indices),
        "indices": anomaly_indices
    }
