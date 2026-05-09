"""
omni_stale_loss.py — STALE Action Detection Loss
Inspired by: STALE (Zero-Shot Temporal Action Detection)
Layer: Compute / AI

Computes the alignment loss between visual features (video segments) 
and text embeddings (action prompts) using InfoNCE/Contrastive loss.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniStaleContrastiveLoss(nn.Module):
    """
    Optimizes the similarity between matching video segments and action labels
    while pushing away non-matching pairs.
    """
    
    def __init__(self, temperature: float = 0.07):
        super().__init__()
        self.temperature = temperature

    def forward(self, 
                visual_embeddings: torch.Tensor, 
                text_embeddings: torch.Tensor, 
                target_matrix: torch.Tensor) -> torch.Tensor:
        """
        visual_embeddings: (Batch * NumSegments, EmbedDim)
        text_embeddings: (NumClasses, EmbedDim)
        target_matrix: (Batch * NumSegments, NumClasses) - 1 if matched, 0 otherwise
        """
        # Normalize embeddings for cosine similarity
        vis_norm = F.normalize(visual_embeddings, p=2, dim=-1)
        text_norm = F.normalize(text_embeddings, p=2, dim=-1)
        
        # Compute similarity matrix (B*S, C)
        logits = torch.matmul(vis_norm, text_norm.t()) / self.temperature
        
        # We treat this as a multi-label classification problem.
        # BCEWithLogitsLoss is appropriate here.
        loss_fn = nn.BCEWithLogitsLoss(reduction='mean')
        
        loss = loss_fn(logits, target_matrix)
        
        return loss

def compute_stale_inference_scores(visual_embeddings: torch.Tensor, text_embeddings: torch.Tensor) -> torch.Tensor:
    """
    Calculates zero-shot probabilities during inference.
    """
    vis_norm = F.normalize(visual_embeddings, p=2, dim=-1)
    text_norm = F.normalize(text_embeddings, p=2, dim=-1)
    
    similarities = torch.matmul(vis_norm, text_norm.t())
    probs = torch.sigmoid(similarities)
    
    return probs
