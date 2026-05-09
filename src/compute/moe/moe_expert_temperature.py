"""
moe_expert_temperature.py — Compute / Inference
Layer: Compute / AI — Dynamic Router Temperature

Controls the "sharpness" of the MoE routing distribution.
A temperature < 1.0 makes the router more decisive (greedy), dropping tokens to fewer experts.
A temperature > 1.0 softens the distribution, encouraging the model to utilize 
niche/rare experts that might otherwise be starved.
"""
import torch
import torch.nn.functional as F

class DynamicRouterTemperature:
    """
    Adjusts the MoE routing softmax temperature dynamically based on the current step
    or the complexity of the input sequence.
    """
    def __init__(self, base_temp: float = 1.0, min_temp: float = 0.5, max_temp: float = 2.0):
        self.base_temp = base_temp
        self.min_temp = min_temp
        self.max_temp = max_temp

    def apply_temperature(self, router_logits: torch.Tensor, sequence_complexity_score: float = None) -> torch.Tensor:
        """
        Applies temperature scaling to the pre-softmax logits.
        
        Args:
            router_logits: (Batch * SeqLen, NumExperts)
            sequence_complexity_score: Optional score from 0.0 to 1.0 indicating how complex the prompt is.
                                       High complexity -> higher temperature (use more experts).
        """
        current_temp = self.base_temp
        
        if sequence_complexity_score is not None:
            # Scale temperature based on complexity
            # 0.0 -> min_temp, 1.0 -> max_temp
            current_temp = self.min_temp + (self.max_temp - self.min_temp) * sequence_complexity_score
            
        # Ensure within bounds
        current_temp = max(self.min_temp, min(self.max_temp, current_temp))
        
        # Scale logits
        scaled_logits = router_logits / current_temp
        
        # Return softened probabilities
        return F.softmax(scaled_logits, dim=-1)

# Example Usage
# temp_manager = DynamicRouterTemperature(base_temp=1.0, min_temp=0.8, max_temp=1.5)
# logits = torch.randn(10, 8) # 10 tokens, 8 experts
# probs = temp_manager.apply_temperature(logits, sequence_complexity_score=0.9)
