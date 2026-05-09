import torch
import torch.nn as nn

# OMNI MOTHER: Dynamic Capacity Scheduler
# Dynamically adjusts expert capacity factors based on moving average of load imbalance.
# Prevents excessive token dropping while maintaining memory efficiency.

class OmniCapacityScheduler:
    def __init__(self, base_capacity: float = 1.0, max_capacity: float = 2.0, alpha: float = 0.9):
        self.base_capacity = base_capacity
        self.max_capacity = max_capacity
        self.current_capacity = base_capacity
        self.alpha = alpha
        
        self.moving_max_load = 0.0

    def step(self, expert_loads: torch.Tensor, num_tokens: int):
        """
        expert_loads: [num_experts] containing token count per expert
        """
        if expert_loads.numel() == 0 or num_tokens == 0:
            return self.current_capacity
            
        num_experts = expert_loads.size(0)
        expected_load = num_tokens / num_experts
        
        max_load = expert_loads.max().item()
        
        # Update moving average
        if self.moving_max_load == 0.0:
            self.moving_max_load = max_load
        else:
            self.moving_max_load = self.alpha * self.moving_max_load + (1 - self.alpha) * max_load
            
        # Calculate needed capacity to accommodate the moving max load
        needed_capacity = self.moving_max_load / expected_load
        
        # Add a small buffer (10%) and clamp
        target_capacity = min(self.max_capacity, max(self.base_capacity, needed_capacity * 1.1))
        
        self.current_capacity = target_capacity
        return self.current_capacity
        
    def get_capacity(self) -> float:
        return self.current_capacity
