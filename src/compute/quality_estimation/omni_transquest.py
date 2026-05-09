"""
omni_transquest.py — Translation Quality Estimation
Inspired by: TransQuest (Transformer based translation quality estimation)
Layer: Compute / AI

Predicts the quality of a machine translation without relying on a reference translation.
"""

import torch
import torch.nn as nn
from typing import Dict, Optional

class OmniTransQuest(nn.Module):
    """Quality Estimation for Machine Translation.
    
    Uses a cross-lingual encoder (e.g., XLM-R) to encode both the source
    sentence and the target translation, outputting a continuous quality score (HTER/DA).
    """

    def __init__(self, hidden_size: int = 768, vocab_size: int = 250000, dropout: float = 0.1):
        super().__init__()
        
        # Token embeddings for cross-lingual vocabulary
        self.embeddings = nn.Embedding(vocab_size, hidden_size, padding_idx=0)
        
        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size, 
            nhead=12, 
            dim_feedforward=3072, 
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=6)
        
        # Regression head for Quality Score (e.g., Direct Assessment score)
        self.regressor = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.Tanh(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1)
        )

    def forward(self, 
                input_ids: torch.Tensor, 
                attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Args:
            input_ids: (B, S) Concatenated [CLS] Source [SEP] Target [SEP]
            attention_mask: (B, S) 1 for tokens, 0 for padding
            
        Returns:
            scores: (B, 1) Predicted quality scores
        """
        # (B, S, D)
        x = self.embeddings(input_ids)
        
        # Invert mask for nn.TransformerEncoder (True means ignore)
        padding_mask = ~attention_mask.bool()
        
        # (B, S, D)
        encoded = self.transformer(x, src_key_padding_mask=padding_mask)
        
        # Extract [CLS] token representation (index 0)
        cls_rep = encoded[:, 0, :]
        
        # Predict score
        scores = self.regressor(cls_rep)
        
        return scores

    def compute_loss(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Pearson Correlation Coefficient Loss + MSE."""
        mse_loss = nn.functional.mse_loss(predictions.squeeze(), targets)
        
        # Pearson correlation
        pred_mean = predictions.mean()
        target_mean = targets.mean()
        
        pred_centered = predictions - pred_mean
        target_centered = targets - target_mean
        
        cov = (pred_centered * target_centered).sum()
        var_pred = (pred_centered ** 2).sum()
        var_target = (target_centered ** 2).sum()
        
        pearson = cov / (torch.sqrt(var_pred * var_target) + 1e-8)
        
        # We want to maximize pearson, so minimize 1 - pearson
        pearson_loss = 1.0 - pearson
        
        return mse_loss + 0.5 * pearson_loss
