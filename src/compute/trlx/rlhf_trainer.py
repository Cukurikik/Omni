from typing import List, Tuple
import numpy as np

# OMNI Python Compute Layer: trlX RLHF Trainer
# Proximal Policy Optimization (PPO) logic for language model fine-tuning.

class PPOTrainer:
    def __init__(self, clip_range: float = 0.2, value_coef: float = 0.5, entropy_coef: float = 0.01):
        self.clip_range = clip_range
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef

    def compute_advantages(self, rewards: np.ndarray, values: np.ndarray, gamma: float = 0.99, lam: float = 0.95) -> np.ndarray:
        """
        Generalized Advantage Estimation (GAE)
        """
        advantages = np.zeros_like(rewards)
        last_gae_lam = 0
        
        # Compute td_errors
        next_values = np.append(values[1:], 0.0)
        delta = rewards + gamma * next_values - values
        
        for t in reversed(range(len(rewards))):
            advantages[t] = delta[t] + gamma * lam * last_gae_lam
            last_gae_lam = advantages[t]
            
        return advantages

    def ppo_loss(self, old_log_probs: np.ndarray, new_log_probs: np.ndarray, advantages: np.ndarray) -> Tuple[float, float]:
        """
        Calculates the PPO clipped surrogate objective.
        Returns (Policy_Loss, Approx_KL)
        """
        ratio = np.exp(new_log_probs - old_log_probs)
        
        # Clipped surrogate objective
        surr1 = ratio * advantages
        surr2 = np.clip(ratio, 1.0 - self.clip_range, 1.0 + self.clip_range) * advantages
        
        policy_loss = -np.mean(np.minimum(surr1, surr2))
        
        # Approximate KL Divergence for monitoring
        approx_kl = 0.5 * np.mean((old_log_probs - new_log_probs) ** 2)
        
        return float(policy_loss), float(approx_kl)

    def train_step(self, old_log_probs: np.ndarray, new_log_probs: np.ndarray, values: np.ndarray, returns: np.ndarray, advantages: np.ndarray) -> dict:
        """
        Executes a single PPO update step.
        """
        pi_loss, kl = self.ppo_loss(old_log_probs, new_log_probs, advantages)
        
        # Value function loss (MSE)
        v_loss = np.mean((returns - values) ** 2)
        
        # Entropy bonus (push probabilities towards uniform to encourage exploration)
        probs = np.exp(new_log_probs)
        entropy = -np.mean(probs * new_log_probs)
        
        total_loss = pi_loss + self.value_coef * v_loss - self.entropy_coef * entropy
        
        return {
            "total_loss": float(total_loss),
            "policy_loss": float(pi_loss),
            "value_loss": float(v_loss),
            "entropy": float(entropy),
            "approx_kl": float(kl)
        }
