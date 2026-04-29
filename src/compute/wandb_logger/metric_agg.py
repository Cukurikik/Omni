import numpy as np

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MetricAggregator:
    def __init__(self):
        pass

    def aggregate_step_metrics(self, raw_metrics: list[float]) -> OmniResult:
        if raw_metrics is None or len(raw_metrics) == 0:
            return OmniResult(error="Cannot aggregate empty metrics")

        # Deterministic mathematical aggregation mimicking W&B internal smoothing (Exponential Moving Average)
        alpha = 0.1
        smoothed = []
        ema = raw_metrics[0]
        
        for val in raw_metrics:
            ema = alpha * val + (1 - alpha) * ema
            smoothed.append(ema)

        summary = {
            "min": float(np.min(raw_metrics)),
            "max": float(np.max(raw_metrics)),
            "mean": float(np.mean(raw_metrics)),
            "latest_smoothed": float(smoothed[-1])
        }

        return OmniResult(value=summary)
