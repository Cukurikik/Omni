"""
moe_anomaly_detector.py — Domain / Security
Layer: Domain / AI — Prompt Anomaly Detection

Malicious users might attempt to craft adversarial prompts designed specifically
to bypass the MoE router and force execution on a highly-restricted or 
expensive expert. This module runs a fast anomaly detection pass on the prompt
embeddings to flag adversarial manipulation before routing.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class PromptAnomalyDetector(nn.Module):
    """
    A lightweight autoencoder. Standard prompts pass through with low reconstruction error.
    Adversarial prompts (which contain bizarre token combinations to fool the router) 
    will have high reconstruction error.
    """
    def __init__(self, embedding_dim: int = 1024, hidden_dim: int = 256):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2)
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, embedding_dim)
        )
        
        self.anomaly_threshold = 0.05
        print("[Anomaly Detector] Initialized Autoencoder for adversarial prompt detection.")

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        encoded = self.encoder(embeddings)
        decoded = self.decoder(encoded)
        return decoded

    def check_for_anomaly(self, embeddings: torch.Tensor) -> bool:
        """
        Returns True if the prompt is deemed anomalous/adversarial.
        """
        self.eval()
        with torch.no_grad():
            reconstructed = self.forward(embeddings)
            
            # Calculate Mean Squared Error reconstruction loss
            mse_loss = F.mse_loss(reconstructed, embeddings, reduction='none')
            # Average across the embedding dimension
            token_errors = mse_loss.mean(dim=-1)
            
            # If any token in the sequence exceeds the threshold, flag it
            max_error = token_errors.max().item()
            
            if max_error > self.anomaly_threshold:
                print(f"[Anomaly Detector] ADVERSARIAL PROMPT DETECTED! Max Error: {max_error:.4f} > {self.anomaly_threshold}")
                return True
                
        return False
