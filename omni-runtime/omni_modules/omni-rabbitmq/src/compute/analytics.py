"""omni-rabbitmq â€” Analytics Engine"""
from typing import List, Dict, Optional
import statistics, math

class AnalyticsEngine:
    @staticmethod
    def mean(values: List[float]) -> float: return statistics.mean(values) if values else 0.0
    @staticmethod
    def median(values: List[float]) -> float: return statistics.median(values) if values else 0.0
    @staticmethod
    def stdev(values: List[float]) -> float: return statistics.stdev(values) if len(values) > 1 else 0.0
    @staticmethod
    def percentile(values: List[float], p: float) -> float:
        s = sorted(values); k = (len(s) - 1) * p; f = math.floor(k); c = math.ceil(k)
        if f == c: return s[int(k)]
        return s[int(f)] * (c - k) + s[int(c)] * (k - f)
    @staticmethod
    def histogram(values: List[float], bins: int = 10) -> Dict:
        mn, mx = min(values), max(values); w = (mx - mn) / bins
        buckets = {f'{mn + i*w:.2f}-{mn + (i+1)*w:.2f}': 0 for i in range(bins)}
        for v in values:
            idx = min(int((v - mn) / w), bins - 1)
            key = list(buckets.keys())[idx]; buckets[key] += 1
        return buckets
    @staticmethod
    def summary(values: List[float]) -> Dict:
        return {'count': len(values), 'mean': AnalyticsEngine.mean(values), 'median': AnalyticsEngine.median(values),
                'stdev': AnalyticsEngine.stdev(values), 'min': min(values), 'max': max(values),
                'p95': AnalyticsEngine.percentile(values, 0.95), 'p99': AnalyticsEngine.percentile(values, 0.99)}