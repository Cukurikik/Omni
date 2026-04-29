# Omni CryptoPredict Time-Series Engine
from typing import List, Dict
import math

def calculate_moving_average(prices: List[float], window: int) -> List[float]:
    """Calculate Simple Moving Average (SMA) for a time series."""
    if len(prices) < window or window <= 0:
        return []
    return [round(sum(prices[i-window:i])/window, 4) for i in range(window, len(prices)+1)]

def calculate_volatility(prices: List[float]) -> float:
    """Calculate historical volatility (standard deviation of returns)."""
    if len(prices) < 2:
        return 0.0
    returns = [(prices[i] - prices[i-1])/prices[i-1] for i in range(1, len(prices))]
    mean_ret = sum(returns) / len(returns)
    variance = sum((r - mean_ret)**2 for r in returns) / len(returns)
    return round(math.sqrt(variance), 4)

def evaluate_timeseries_forecast(predictions: List[float], actuals: List[float]) -> Dict[str, float]:
    """Evaluate financial time-series forecasting metrics like MAPE."""
    if not predictions or len(predictions) != len(actuals):
        return {"mape": 0.0, "directional_accuracy": 0.0}
        
    mape_sum = sum(abs((a - p) / max(a, 1e-8)) for p, a in zip(predictions, actuals))
    mape = (mape_sum / len(actuals)) * 100
    
    correct_dir = 0
    for i in range(1, len(actuals)):
        actual_dir = actuals[i] - actuals[i-1]
        pred_dir = predictions[i] - actuals[i-1] # Assume prediction was made at i-1
        if (actual_dir > 0 and pred_dir > 0) or (actual_dir < 0 and pred_dir < 0):
            correct_dir += 1
            
    dir_acc = correct_dir / max(len(actuals)-1, 1)
    
    return {
        "mape_percentage": round(mape, 4),
        "directional_accuracy": round(dir_acc, 4)
    }
