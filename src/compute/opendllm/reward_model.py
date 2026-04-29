import numpy as np
from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class RewardModel:
    def calculate_reward(self, generated_code: str, test_passed: bool) -> OmniResult:
        if not generated_code:
            return OmniResult(None, "Generated code is empty")
            
        try:
            # Python reward model calculation for Open-dLLM
            reward = 1.0 if test_passed else -0.5
            
            return OmniResult(reward)
        except Exception as e:
            return OmniResult(None, str(e))
