"""
OMNI Transformer — Next Sentence Prediction for Pretraining
NSP head for BERT-style pretraining.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict


class NSPHead(nn.Module):
    """Next Sentence Prediction classification head."""
    def __init__(self, embed_dim: int):
        super().__init__()
        self.classifier = nn.Linear(embed_dim, 2)

    def forward(self, pooled_output: torch.Tensor, labels=None) -> Dict:
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            loss = F.cross_entropy(logits, labels)
        return {"logits": logits, "loss": loss}
