import torch
import torch.nn.functional as F
from typing import Tuple, Optional

# OMNI LLM-RL: Direct Preference Optimization (DPO) Loss
# Reward-free alignment for LLMs using paired preferences.
# Source: changyeyu/LLM-RL-Visualized

class DPOError(Exception):
    pass

def compute_dpo_loss(
    policy_chosen_logps: torch.Tensor,
    policy_rejected_logps: torch.Tensor,
    reference_chosen_logps: torch.Tensor,
    reference_rejected_logps: torch.Tensor,
    beta: float = 0.1
) -> Tuple[Optional[torch.Tensor], Optional[DPOError]]:
    """
    Computes the DPO loss for a batch of chosen/rejected pairs.
    
    Args:
        policy_chosen_logps: Log probs of chosen responses under current policy.
        policy_rejected_logps: Log probs of rejected responses under current policy.
        reference_chosen_logps: Log probs of chosen responses under reference model.
        reference_rejected_logps: Log probs of rejected responses under reference model.
        beta: Temperature parameter controlling deviation from reference model.
    """
    try:
        if not (policy_chosen_logps.shape == policy_rejected_logps.shape == 
                reference_chosen_logps.shape == reference_rejected_logps.shape):
            return None, DPOError("All input log-probability tensors must have the same shape.")

        # Compute implicit reward difference from current policy
        policy_logratios = policy_chosen_logps - policy_rejected_logps
        
        # Compute implicit reward difference from reference policy
        reference_logratios = reference_chosen_logps - reference_rejected_logps
        
        # Compute DPO logits: beta * (policy_logratio - ref_logratio)
        logits = policy_logratios - reference_logratios
        
        # The loss is the negative log-sigmoid of the scaled logits
        loss = -F.logsigmoid(beta * logits).mean()
        
        # Optional: return the implied reward margins for logging
        # reward_margin = beta * logits.mean().detach()
        
        return loss, None

    except Exception as e:
        return None, DPOError(f"DPO Loss computation failed: {str(e)}")
