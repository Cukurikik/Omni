"""
moe_router_z_loss.py — Compute / Training
Layer: Compute / AI — Router Z-Loss Regularization

Implements Router Z-Loss (from ST-MoE / Mesh-TensorFlow).
Without this, router logits can grow unboundedly large during training,
causing precision issues (NaNs) and unstable routing decisions.
Z-Loss penalizes large un-softmaxed logits.
"""
import torch
import torch.nn.functional as F

def compute_router_z_loss(router_logits: torch.Tensor) -> torch.Tensor:
    """
    Computes the Z-Loss for MoE router logits.
    
    Formula: Z-loss = log(sum(exp(logits)))^2
    Or simply the square of the log-sum-exp of the logits.
    
    Args:
        router_logits: Tensor of shape (Batch * SeqLen, NumExperts)
                       These are the raw pre-softmax outputs of the gate.
                       
    Returns:
        Scalar tensor representing the Z-Loss penalty.
    """
    # Use PyTorch's numerically stable logsumexp
    # logsumexp = torch.logsumexp(router_logits, dim=-1) # Shape: (Batch * SeqLen)
    
    # Calculate log_z
    log_z = torch.logsumexp(router_logits, dim=-1)
    
    # Square the log_z to penalize both large positive and large negative 
    # absolute magnitudes of the softmax denominator.
    z_loss = torch.mean(log_z ** 2)
    
    return z_loss

class MoERouterWithZLoss(torch.nn.Module):
    """
    Example integration of a Router that returns both probabilities and the Z-Loss penalty.
    """
    def __init__(self, hidden_dim: int, num_experts: int, z_loss_coef: float = 1e-3):
        super().__init__()
        self.gate = torch.nn.Linear(hidden_dim, num_experts, bias=False)
        self.z_loss_coef = z_loss_coef

    def forward(self, x: torch.Tensor):
        # x: (Batch, SeqLen, Hidden)
        logits = self.gate(x)
        
        # Calculate routing probabilities
        routing_probs = F.softmax(logits, dim=-1)
        
        # Calculate Z-Loss only if training
        if self.training:
            # Flatten to 2D
            flat_logits = logits.view(-1, logits.size(-1))
            z_loss_penalty = compute_router_z_loss(flat_logits) * self.z_loss_coef
        else:
            z_loss_penalty = torch.tensor(0.0, device=logits.device)
            
        return routing_probs, z_loss_penalty
