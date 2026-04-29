# LLM Finetuning Trainer
from typing import Optional, Generic, TypeVar, Dict

T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class DPOFinetuner:
    def __init__(self, beta: float = 0.1):
        self.beta = beta

    def compute_dpo_loss(self, pi_logps_chosen: float, pi_logps_rejected: float, 
                         ref_logps_chosen: float, ref_logps_rejected: float) -> OmniResult[float, str]:
        
        pi_logratios = pi_logps_chosen - pi_logps_rejected
        ref_logratios = ref_logps_chosen - ref_logps_rejected
        
        logits = pi_logratios - ref_logratios
        
        # Binary cross entropy loss for DPO
        import math
        try:
            loss = -math.log(1.0 / (1.0 + math.exp(-self.beta * logits)))
            return OmniResult(value=loss)
        except OverflowError:
            return OmniResult(error="Math overflow in sigmoid")
