import torch
from typing import Tuple, Optional

# OMNI LLM-RL: PPO Clipping Loss
# Proximal Policy Optimization (PPO) clip objective for RLHF.
# Source: changyeyu/LLM-RL-Visualized

class PPOError(Exception):
    pass

def compute_ppo_loss(
    logprobs: torch.Tensor,
    old_logprobs: torch.Tensor,
    advantages: torch.Tensor,
    clip_range: float = 0.2
) -> Tuple[Optional[torch.Tensor], Optional[PPOError]]:
    """
    Computes the PPO clipped surrogate objective.
    Monadic error handling for tensor shape validation.
    
    Args:
        logprobs: Tensor of shape (batch_size, seq_len)
        old_logprobs: Tensor of shape (batch_size, seq_len)
        advantages: Tensor of shape (batch_size, seq_len)
        
    Returns:
        loss: Scalar tensor representing the PPO policy loss (to be minimized).
    """
    try:
        if logprobs.shape != old_logprobs.shape or logprobs.shape != advantages.shape:
            return None, PPOError("Tensor shapes must match for logprobs, old_logprobs, and advantages.")
            
        # Probability ratio r_t(theta) = exp(log_prob - old_log_prob)
        ratio = torch.exp(logprobs - old_logprobs)
        
        # Unclipped objective
        surr1 = ratio * advantages
        
        # Clipped objective
        surr2 = torch.clamp(ratio, 1.0 - clip_range, 1.0 + clip_range) * advantages
        
        # We want to maximize the surrogate, so we return the negative mean for gradient descent
        policy_loss = -torch.min(surr1, surr2).mean()
        
        return policy_loss, None
        
    except Exception as e:
        return None, PPOError(f"PPO Loss computation failed: {str(e)}")
