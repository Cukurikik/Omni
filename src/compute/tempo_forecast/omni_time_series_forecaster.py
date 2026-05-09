# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo DC-research/TEMPO + ServiceNow/TACTiS
# @omni-description TEMPO time series forecaster with decomposition and copulas.

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class TSConfig:
    d_model: int = 768
    n_heads: int = 12
    forecast_horizon: int = 96
    lookback: int = 336
    n_prompts: int = 16
    decompose_kernel: int = 25

class MovingAvgDecompose:
    def __init__(self, k: int = 25):
        self.pad = k // 2
    def decompose(self, x: List[float]) -> Tuple[List[float], List[float], List[float]]:
        n = len(x)
        trend = [sum(x[max(0,i-self.pad):min(n,i+self.pad+1)])/(min(n,i+self.pad+1)-max(0,i-self.pad)) for i in range(n)]
        seasonal = [x[i] - trend[i] for i in range(n)]
        residual = [0.0]*n
        return trend, seasonal, residual

class TempoForecaster:
    def __init__(self, config: TSConfig):
        self.config = config
        self.decomposer = MovingAvgDecompose(config.decompose_kernel)
    def forecast(self, series: List[List[float]]) -> List[List[float]]:
        results = []
        for s in series:
            t, sea, r = self.decomposer.decompose(s)
            slope = (t[-1]-t[max(0,len(t)-10)])/min(10,len(t)) if len(t)>1 else 0
            fc = [t[-1]+slope*(i+1)+sea[i%len(sea)] for i in range(self.config.forecast_horizon)]
            results.append(fc)
        return results
