"""
omni_coco_lm_loss.py — COCO-LM Correcting and Contrasting Objective
Inspired by: COCO-LM (Correcting and Contrasting Text Sequences)
Layer: Compute / AI

Implementation of the COCO-LM pretraining objective which introduces 
Sequence Correcting and Sequence Contrasting to improve representation learning.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple

class OmniCOCOLMLoss(nn.Module):
    """COCO-LM Pretraining Objectives.
    
    Combines Masked Language Modeling (MLM), Sequence Correcting (SC),
    and Sequence Contrasting (SCL).
    """

    def __init__(self, vocab_size: int, hidden_size: int, temperature: float = 0.05):
        super().__init__()
        self.vocab_size = vocab_size
        self.temperature = temperature
        
        # Projection for Sequence Contrasting
        self.scl_projection = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.GELU(),
            nn.Linear(hidden_size, hidden_size)
        )

    def sequence_correcting_loss(self, 
                                 generator_logits: torch.Tensor, 
                                 discriminator_hidden: torch.Tensor,
                                 corrupted_tokens: torch.Tensor,
                                 original_tokens: torch.Tensor,
                                 correct_mask: torch.Tensor) -> torch.Tensor:
        """Compute Sequence Correcting (SC) Loss.
        
        The model tries to predict the original tokens from the corrupted tokens,
        focusing specifically on tokens that were altered by the generator.
        
        Args:
            generator_logits: (B, N, V) logits from generator (not directly used here, but part of framework)
            discriminator_hidden: (B, N, D) representations from the main model
            corrupted_tokens: (B, N) input tokens (some are generated replacements)
            original_tokens: (B, N) original ground truth tokens
            correct_mask: (B, N) boolean mask indicating which tokens were replaced
            
        Returns:
            sc_loss: scalar loss
        """
        # Linear head for token prediction
        if not hasattr(self, 'sc_head'):
            self.sc_head = nn.Linear(discriminator_hidden.size(-1), self.vocab_size, bias=False)
            self.sc_head.to(discriminator_hidden.device)
            
        logits = self.sc_head(discriminator_hidden)
        
        # Only compute loss on tokens that were corrupted/replaced
        active_logits = logits[correct_mask]
        active_labels = original_tokens[correct_mask]
        
        if active_labels.numel() == 0:
            return torch.tensor(0.0, device=logits.device, requires_grad=True)
            
        return F.cross_entropy(active_logits, active_labels)

    def sequence_contrasting_loss(self, 
                                  original_cls: torch.Tensor, 
                                  corrupted_cls: torch.Tensor) -> torch.Tensor:
        """Compute Sequence Contrasting (SCL) Loss.
        
        Aligns representations of original sequence crops and their 
        generator-corrupted variants.
        
        Args:
            original_cls: (B, D) representation of original text crop
            corrupted_cls: (B, D) representation of corrupted text crop
            
        Returns:
            scl_loss: scalar contrastive loss
        """
        B = original_cls.size(0)
        
        # Project representations
        z_org = F.normalize(self.scl_projection(original_cls), dim=-1)
        z_cor = F.normalize(self.scl_projection(corrupted_cls), dim=-1)
        
        # Contrastive similarities (B, B)
        # z_org_i dot z_cor_j
        sim_matrix = torch.matmul(z_org, z_cor.t()) / self.temperature
        
        # Target is identity matrix (i=j are positive pairs)
        labels = torch.arange(B, dtype=torch.long, device=sim_matrix.device)
        
        loss_o2c = F.cross_entropy(sim_matrix, labels)
        loss_c2o = F.cross_entropy(sim_matrix.t(), labels)
        
        return (loss_o2c + loss_c2o) / 2.0

    def forward(self, 
                discriminator_hidden: torch.Tensor,
                corrupted_tokens: torch.Tensor,
                original_tokens: torch.Tensor,
                correct_mask: torch.Tensor,
                original_cls: torch.Tensor,
                corrupted_cls: torch.Tensor,
                alpha_sc: float = 1.0,
                alpha_scl: float = 1.0) -> Dict[str, torch.Tensor]:
        """Compute full COCO-LM objective."""
        
        sc_loss = self.sequence_correcting_loss(
            None, discriminator_hidden, corrupted_tokens, original_tokens, correct_mask
        )
        
        scl_loss = self.sequence_contrasting_loss(original_cls, corrupted_cls)
        
        total_loss = alpha_sc * sc_loss + alpha_scl * scl_loss
        
        return {
            "loss": total_loss,
            "sc_loss": sc_loss,
            "scl_loss": scl_loss
        }
