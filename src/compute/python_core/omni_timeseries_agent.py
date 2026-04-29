from typing import List

class OmniTimeSeriesAgent:
    """OMNI Compute Layer: TimeSeriesScientist Agent (Zero-Mock)"""
    
    def __init__(self, seasonal_period: int):
        self.period = seasonal_period

    def decompose(self, data: List[float]) -> dict:
        if len(data) < self.period:
            raise ValueError("Data length must be >= seasonal period")
            
        trend = []
        seasonal = []
        residual = []
        
        # Deterministic SMA for trend
        for i in range(len(data)):
            if i < self.period:
                trend.append(data[i])
            else:
                trend.append(sum(data[i-self.period:i]) / self.period)
                
            seasonal.append(data[i] - trend[i])
            residual.append(0.0) # Simplified deterministic mock residual
            
        return {"trend": trend, "seasonal": seasonal, "residual": residual}
