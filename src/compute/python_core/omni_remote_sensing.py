# Omni Remote Sensing Agent Engine
# Ref: PolyX-Research/Awesome-Remote-Sensing-Agents
import math
from typing import List, Tuple

def calculate_ndvi(nir_band: List[float], red_band: List[float]) -> List[float]:
    """Calculate Normalized Difference Vegetation Index from NIR and Red spectral bands."""
    if len(nir_band) != len(red_band) or not nir_band:
        return []
        
    ndvi = []
    for n, r in zip(nir_band, red_band):
        denominator = n + r
        val = (n - r) / denominator if denominator != 0 else 0.0
        ndvi.append(round(val, 4))
    return ndvi

def detect_geospatial_anomalies(ndvi_series: List[float], historical_mean: float, threshold: float = 0.2) -> List[int]:
    """Detect anomalies (e.g., deforestation, drought) based on NDVI deviation."""
    anomalies = []
    for idx, val in enumerate(ndvi_series):
        if abs(val - historical_mean) > threshold:
            anomalies.append(idx)
    return anomalies

def analyze_remote_sensing_region(nir: List[float], red: List[float], hist_mean: float) -> dict:
    ndvi = calculate_ndvi(nir, red)
    if not ndvi:
        return {"mean_ndvi": 0.0, "anomaly_count": 0}
        
    mean_ndvi = sum(ndvi) / len(ndvi)
    anomalies = detect_geospatial_anomalies(ndvi, hist_mean)
    
    return {
        "mean_ndvi": round(mean_ndvi, 4),
        "anomaly_count": len(anomalies),
        "health_score": round(max(0.0, min(1.0, (mean_ndvi + 1) / 2)), 4)
    }
