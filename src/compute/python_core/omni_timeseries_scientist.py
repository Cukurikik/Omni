# Omni TimeSeriesScientist
# Compute Layer: LLM-powered agentic time series analysis.
# Ref: Y-Research-SBU/TimeSeriesScientist
import math
from typing import List, Dict, Tuple

def moving_average(data: List[float], window: int) -> List[float]:
    if window <= 0 or not data:
        return []
    result = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        result.append(sum(data[start:i+1]) / (i - start + 1))
    return result

def detect_anomalies_zscore(data: List[float], threshold: float = 3.0) -> List[int]:
    if len(data) < 2:
        return []
    mean = sum(data) / len(data)
    std = math.sqrt(sum((x - mean) ** 2 for x in data) / len(data))
    if std == 0:
        return []
    return [i for i, x in enumerate(data) if abs((x - mean) / std) > threshold]

def seasonal_decompose_additive(data: List[float], period: int) -> Dict:
    if period <= 0 or len(data) < period * 2:
        return {"status": "error", "message": "OMNI_ERR: Insufficient data for decomposition"}
    trend = moving_average(data, period)
    seasonal = [0.0] * len(data)
    for i in range(period):
        cycle_vals = [data[j] - trend[j] for j in range(i, len(data), period) if j < len(trend)]
        avg = sum(cycle_vals) / len(cycle_vals) if cycle_vals else 0.0
        for j in range(i, len(data), period):
            seasonal[j] = avg
    residual = [data[i] - trend[i] - seasonal[i] for i in range(len(data))]
    return {"status": "ok", "trend": trend, "seasonal": seasonal, "residual": residual}

def forecast_naive(data: List[float], steps: int) -> List[float]:
    if not data or steps <= 0:
        return []
    last = data[-1]
    return [last] * steps

def autocorrelation(data: List[float], lag: int) -> float:
    n = len(data)
    if n < lag + 1:
        return 0.0
    mean = sum(data) / n
    var = sum((x - mean) ** 2 for x in data) / n
    if var == 0:
        return 0.0
    cov = sum((data[i] - mean) * (data[i + lag] - mean) for i in range(n - lag)) / n
    return cov / var
