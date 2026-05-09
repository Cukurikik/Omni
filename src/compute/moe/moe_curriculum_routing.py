"""
moe_curriculum_routing.py — Curriculum Learning for MoE Routers
Layer: Compute / AI — Training Dynamics

Adjusts routing parameters (temperature, capacity factor) dynamically
during training. Early in training, high temperature encourages exploration
and prevents premature expert specialization. Later, it cools down
to allow hard specialization.
"""
import torch
import torch.nn as nn
import math


class CurriculumRouterSchedule:
    """Manages the curriculum schedules for MoE router hyperparameters."""
    def __init__(self, 
                 total_steps: int, 
                 warmup_steps: int = 1000,
                 init_temperature: float = 2.0,
                 min_temperature: float = 0.5,
                 init_capacity: float = 2.0,
                 min_capacity: float = 1.05):
        self.total_steps = total_steps
        self.warmup_steps = warmup_steps
        
        self.init_temp = init_temperature
        self.min_temp = min_temperature
        
        self.init_cap = init_capacity
        self.min_cap = min_capacity
        
        self.current_step = 0

    def step(self):
        self.current_step += 1

    def get_temperature(self) -> float:
        """Cosine annealing schedule for softmax temperature."""
        if self.current_step < self.warmup_steps:
            # Constant high temp during warmup
            return self.init_temp
        
        progress = (self.current_step - self.warmup_steps) / max(1, self.total_steps - self.warmup_steps)
        progress = min(1.0, max(0.0, progress))
        
        # Cosine decay
        cosine_decay = 0.5 * (1 + math.cos(math.pi * progress))
        return self.min_temp + (self.init_temp - self.min_temp) * cosine_decay

    def get_capacity_factor(self) -> float:
        """Linear decay for capacity factor (allow dropping later in training)."""
        if self.current_step < self.warmup_steps:
            return self.init_cap
            
        progress = (self.current_step - self.warmup_steps) / max(1, self.total_steps - self.warmup_steps)
        progress = min(1.0, max(0.0, progress))
        
        return self.init_cap - (self.init_cap - self.min_cap) * progress


class CurriculumGating(nn.Module):
    """Wrapper around linear gate that applies the curriculum temperature."""
    def __init__(self, dim: int, num_experts: int, schedule: CurriculumRouterSchedule):
        super().__init__()
        self.gate = nn.Linear(dim, num_experts, bias=False)
        self.schedule = schedule

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        logits = self.gate(hidden_states)
        
        if self.training:
            temp = self.schedule.get_temperature()
            logits = logits / temp
            self.schedule.step()
            
        return logits
