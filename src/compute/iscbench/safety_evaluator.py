from typing import Any, List

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class InternalSafetyEvaluator:
    def __init__(self, threshold: float = 0.9):
        self.threshold = threshold

    def evaluate_collapse_risk(self, prompt: str, generated_text: str) -> OmniResult:
        if not prompt or not generated_text:
            return OmniResult(None, "Inputs cannot be empty")
            
        try:
            # PII detection and internal safety collapse probability
            sensitive_patterns = ["password", "api_key", "secret", "ssn"]
            matches = sum(1 for p in sensitive_patterns if p in generated_text.lower())
            
            risk_score = min(1.0, (matches * 0.25))
            is_collapsed = risk_score > self.threshold
            
            return OmniResult({"risk_score": risk_score, "is_collapsed": is_collapsed})
        except Exception as e:
            return OmniResult(None, str(e))
