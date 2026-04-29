from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class SkillEvaluator:
    def evaluate_execution(self, task_result: str, expected: str) -> OmniResult:
        if not task_result or not expected:
            return OmniResult(None, "Missing evaluation inputs")
            
        try:
            # Simple string matching as a placeholder for LLM semantic evaluation
            score = 1.0 if expected.lower() in task_result.lower() else 0.0
            return OmniResult({"score": score, "pass": score > 0.8})
        except Exception as e:
            return OmniResult(None, str(e))
