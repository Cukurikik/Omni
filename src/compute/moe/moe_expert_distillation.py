"""
moe_expert_distillation.py — Compute / Optimization
Layer: Compute / AI — Expert Knowledge Distillation

When an expert becomes too large or slow (e.g., an FP16 100B parameter expert),
this module orchestrates Knowledge Distillation to train a smaller 4-bit or 
low-rank "Sub-Expert" to mimic the behavior of the massive "Teacher Expert".
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ExpertDistiller:
    def __init__(self, temperature: float = 2.0, alpha: float = 0.5):
        self.temperature = temperature
        self.alpha = alpha
        print(f"[Distillation] Initialized MoE Expert Distiller (Temp: {temperature}, Alpha: {alpha})")

    def distillation_loss(self, student_logits: torch.Tensor, teacher_logits: torch.Tensor, target_labels: torch.Tensor):
        """
        Computes the combined loss: 
        Soft-target loss (matching teacher probabilities) + Hard-target loss (matching true labels).
        """
        # Soft targets (Teacher's softened probabilities)
        soft_targets = F.softmax(teacher_logits / self.temperature, dim=-1)
        student_log_probs = F.log_softmax(student_logits / self.temperature, dim=-1)
        
        # KL Divergence between softened student and teacher
        distillation_loss = F.kl_div(student_log_probs, soft_targets, reduction='batchmean') * (self.temperature ** 2)
        
        # Hard targets (Standard Cross Entropy)
        # Assuming classification/token prediction for the expert
        student_ce_loss = F.cross_entropy(student_logits, target_labels)
        
        # Combined Loss
        total_loss = (self.alpha * distillation_loss) + ((1.0 - self.alpha) * student_ce_loss)
        return total_loss

    def train_step(self, student_expert: nn.Module, teacher_expert: nn.Module, inputs: torch.Tensor, targets: torch.Tensor, optimizer: torch.optim.Optimizer):
        """
        Executes one forward/backward pass for distilling the teacher into the student.
        """
        student_expert.train()
        teacher_expert.eval() # Teacher is always frozen
        
        with torch.no_grad():
            teacher_outputs = teacher_expert(inputs)
            
        student_outputs = student_expert(inputs)
        
        loss = self.distillation_loss(student_outputs, teacher_outputs, targets)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        return loss.item()
