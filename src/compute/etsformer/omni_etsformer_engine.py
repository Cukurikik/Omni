"""
@omni-layer Compute | @omni-source lucidrains/ETSformer-pytorch
@omni-description ETSformer engine: exponential smoothing attention for time
series forecasting with level, growth, and seasonality decomposition.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Tuple

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniETSformer:
    def __init__(self, d=64, n_heads=4, seq_len=96, pred_len=24, n_seasons=4):
        self.d = d; self.n_heads = n_heads; self.seq_len = seq_len
        self.pred_len = pred_len; self.n_seasons = n_seasons
        self.alpha = [0.3]*n_heads  # smoothing factors per head

    def exponential_smoothing(self, series: List[float], alpha: float) -> Tuple[List[float], List[float]]:
        level = [series[0]]
        growth = [0.0]
        for t in range(1, len(series)):
            l = alpha * series[t] + (1 - alpha) * (level[-1] + growth[-1])
            g = 0.3 * (l - level[-1]) + 0.7 * growth[-1]
            level.append(l); growth.append(g)
        return level, growth

    def seasonal_decompose(self, series: List[float]) -> List[float]:
        period = max(1, len(series) // max(self.n_seasons, 1))
        seasonal = [0.0]*len(series)
        for i in range(len(series)):
            group = [series[j] for j in range(i % period, len(series), period)]
            seasonal[i] = sum(group)/len(group) if group else 0
        detrended = [series[i] - seasonal[i] for i in range(len(series))]
        return detrended

    def frequency_attention(self, series: List[float]) -> List[float]:
        n = len(series)
        freqs = []
        for k in range(n//2 + 1):
            re = sum(series[t]*math.cos(2*math.pi*k*t/n) for t in range(n)) / n
            im = sum(series[t]*math.sin(2*math.pi*k*t/n) for t in range(n)) / n
            freqs.append(math.sqrt(re*re + im*im))
        top_k = min(5, len(freqs))
        indices = sorted(range(len(freqs)), key=lambda i: -freqs[i])[:top_k]
        filtered = [0.0]*n
        for k in indices:
            for t in range(n):
                filtered[t] += freqs[k]*math.cos(2*math.pi*k*t/n)
        return filtered

    def forecast(self, series: List[float]) -> OmniResult:
        try:
            if len(series) < 4: return OmniResult(error=Exception("Series too short"))
            forecasts_per_head = []
            for h in range(self.n_heads):
                level, growth = self.exponential_smoothing(series, self.alpha[h])
                last_l, last_g = level[-1], growth[-1]
                pred = [last_l + (i+1)*last_g for i in range(self.pred_len)]
                forecasts_per_head.append(pred)
            ensemble = [sum(f[i] for f in forecasts_per_head)/self.n_heads for i in range(self.pred_len)]
            freq_component = self.frequency_attention(series)
            return OmniResult(data={"forecast": ensemble, "n_steps": self.pred_len, "last_level": level[-1], "last_growth": growth[-1], "freq_magnitudes": freq_component[:5]})
        except Exception as e: return OmniResult(error=e)
