from __future__ import annotations
from src.compute.python_core.omni_base_engine import Result, Ok, Err
from typing import Dict, Any, List

class OmniSuomiPervasiveEngine:
    """OMNI Zero-Prod Production Implementation for OmniSuomiPervasiveEngine."""
    
    def __init__(self, alpha: float = 0.5) -> None:
        self.alpha = alpha
        
    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniSuomiPervasiveEngine",
            "status": "operational",
            "batch": 51,
            "semester": 11,
            "domain": "Pervasive IoT Exponential Moving Average"
        }
        
    def calculate_ema_anomalies(self, stream: List[float], threshold: float) -> Result[List[Dict[str, Any]], Exception]:
        """
        Analyzes a pervasive IoT stream (like SPA temperature metrics) extracting anomalous deviations
        using Exponential Moving Average (EMA).
        """
        try:
            if not stream:
                return Err(ValueError("No pervasive data node provided"))
            if self.alpha <= 0.0 or self.alpha > 1.0:
                return Err(ValueError("Alpha momentum index must strictly bound (0, 1]"))
            if threshold <= 0.0:
                return Err(ValueError("Anomaly bounds must be strictly positive"))
                
            anomalies = []
            ema = stream[0]
            
            for idx, val in enumerate(stream):
                ema = (val * self.alpha) + (ema * (1.0 - self.alpha))
                deviation = abs(val - ema)
                if deviation > threshold:
                    anomalies.append({
                        "index": idx,
                        "value": val,
                        "ema": round(ema, 4),
                        "deviation": round(deviation, 4)
                    })
                    
            return Ok(anomalies)
        except Exception as e:
            return Err(e)
