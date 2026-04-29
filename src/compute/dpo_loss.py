# OMNI Compute Layer - DPO Loss
import numpy as np

class DPOError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def compute_dpo_loss(policy_chosen_logps: float, policy_rejected_logps: float, 
                    ref_chosen_logps: float, ref_rejected_logps: float, beta: float) -> Result:
    """Computes the Direct Preference Optimization (DPO) loss."""
    try:
        if beta <= 0:
            return Result(error=DPOError("Beta must be positive"))
            
        policy_logratios = policy_chosen_logps - policy_rejected_logps
        ref_logratios = ref_chosen_logps - ref_rejected_logps
        
        logits = policy_logratios - ref_logratios
        loss = -np.log(1 / (1 + np.exp(-beta * logits)))
        
        return Result(value={"loss": float(loss), "reward_margin": float(logits)})
    except Exception as e:
        return Result(error=DPOError(f"DPO Compute failed: {str(e)}"))
