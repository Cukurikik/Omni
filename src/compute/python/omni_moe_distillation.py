import torch
import torch.nn.functional as F

# OMNI MOTHER: Sparse MoE to Dense Distillation
# Distills knowledge from a massive sparse MoE into a dense model for edge deployment

class OmniMoEDistillation:
    def __init__(self, teacher_moe, student_dense, temperature: float = 2.0):
        self.teacher = teacher_moe
        self.student = student_dense
        self.temperature = temperature

    def compute_loss(self, x: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            teacher_logits = self.teacher(x)
            
        student_logits = self.student(x)
        
        # Soft target loss (KL Divergence)
        distillation_loss = F.kl_div(
            F.log_softmax(student_logits / self.temperature, dim=-1),
            F.softmax(teacher_logits / self.temperature, dim=-1),
            reduction='batchmean'
        ) * (self.temperature ** 2)
        
        # Hard target loss
        task_loss = F.cross_entropy(student_logits, target)
        
        return 0.5 * distillation_loss + 0.5 * task_loss
