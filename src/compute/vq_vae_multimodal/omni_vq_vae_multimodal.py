from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI Multimodal VQ-VAE Engine — Compute Layer
# Absorbing CompletedProjects/Multimodal_VQ-VAE
# Vector Quantized Variational Autoencoder merging vision and text latents.

@dataclass
class VqVaeResult:
    ok: bool
    quantized_latents: np.ndarray = None
    perplexity: float = 0.0
    error: str = None

class OmniVqVaeMultimodal:
    def __init__(self, num_embeddings: int = 512, embedding_dim: int = 64):
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.quantizations = 0
        np.random.seed(101)
        self.codebook = np.random.randn(num_embeddings, embedding_dim) * 0.1

    def quantize(self, z_e: np.ndarray) -> VqVaeResult:
        """
        z_e: (B, Dim). Continuous latent representations.
        Maps z_e to discrete codebook vectors.
        """
        if z_e.ndim != 2 or z_e.shape[-1] != self.embedding_dim:
            return VqVaeResult(False, error="VqVaeError: Mismatched latent dimension against codebook")
            
        try:
            self.quantizations += 1
            
            # Compute distances: (B, K)
            # z_e^2 + codebook^2 - 2 * z_e * codebook
            z_e_sq = np.sum(z_e ** 2, axis=1, keepdims=True)
            cb_sq = np.sum(self.codebook ** 2, axis=1)
            dist = z_e_sq + cb_sq - 2 * np.dot(z_e, self.codebook.T)
            
            # Find nearest embedding index
            encoding_indices = np.argmin(dist, axis=1)
            
            # Gather quantized vectors
            z_q = self.codebook[encoding_indices]
            
            # Perplexity (measures codebook usage)
            # Flatten indices
            encodings = np.eye(self.num_embeddings)[encoding_indices]
            avg_probs = np.mean(encodings, axis=0)
            perplexity = float(np.exp(-np.sum(avg_probs * np.log(avg_probs + 1e-10))))
            
            return VqVaeResult(True, quantized_latents=z_q, perplexity=perplexity)
            
        except Exception as e:
            return VqVaeResult(False, error=f"VqVaeError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniVqVaeMultimodal", "quantizations": self.quantizations, "status": "Operational"}
