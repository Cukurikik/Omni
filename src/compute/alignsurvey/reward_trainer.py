from typing import Any
import numpy as np

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class RewardModelTrainer:
    def __init__(self, learning_rate: float = 1e-4):
        self.lr = learning_rate

    def compute_loss(self, chosen_rewards: np.ndarray, rejected_rewards: np.ndarray) -> OmniResult:
        if chosen_rewards is None or rejected_rewards is None:
            return OmniResult(None, "Invalid reward inputs")
            
        try:
            # Bradley-Terry model loss calculation
            loss = -np.log(1.0 / (1.0 + np.exp(rejected_rewards - chosen_rewards)))
            return OmniResult(np.mean(loss))
        except Exception as e:
            return OmniResult(None, str(e))
