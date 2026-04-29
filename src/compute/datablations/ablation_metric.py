from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class AblationMetric:
    def calculate_impact(self, baseline_loss: float, ablation_loss: float) -> OmniResult:
        if baseline_loss < 0 or ablation_loss < 0:
            return OmniResult(None, "Invalid loss inputs")
            
        try:
            # Python distributed metrics computing the isolated impact of data subsets
            impact_score = ablation_loss - baseline_loss
            
            return OmniResult(impact_score)
        except Exception as e:
            return OmniResult(None, str(e))
