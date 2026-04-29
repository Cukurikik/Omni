from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    class nn: Module = object

# OMNI PerceiverIO Engine — Compute Layer
# Absorbing JOBR0/PerceiverIO_Pytorch: Adaptation of Deepmind's PerceiverIO
# O(NM) Cross-Attention for flexible inputs mapping to latent array.

@dataclass
class PerceiverResult:
    ok: bool
    latent_representation: Any = None
    output_array: Any = None
    error: str = None

class CrossAttention(nn.Module if TORCH_AVAILABLE else object):
    def __init__(self, input_dim: int, latent_dim: int, heads: int = 8):
        if TORCH_AVAILABLE:
            super().__init__()
            self.heads = heads
            self.q_proj = nn.Linear(latent_dim, latent_dim)
            self.k_proj = nn.Linear(input_dim, latent_dim)
            self.v_proj = nn.Linear(input_dim, latent_dim)
            self.out_proj = nn.Linear(latent_dim, latent_dim)

    def forward(self, inputs: 'torch.Tensor', latents: 'torch.Tensor') -> 'torch.Tensor':
        B, N, _ = inputs.shape
        B, M, D = latents.shape
        H = self.heads
        hd = D // H

        q = self.q_proj(latents).view(B, M, H, hd).transpose(1, 2) # (B, H, M, hd)
        k = self.k_proj(inputs).view(B, N, H, hd).transpose(1, 2)  # (B, H, N, hd)
        v = self.v_proj(inputs).view(B, N, H, hd).transpose(1, 2)

        attn = torch.matmul(q, k.transpose(-2, -1)) / (hd ** 0.5)
        probs = torch.softmax(attn, dim=-1)
        
        out = torch.matmul(probs, v).transpose(1, 2).contiguous().view(B, M, D)
        return latents + self.out_proj(out)

class OmniPerceiverIoEngine(nn.Module if TORCH_AVAILABLE else object):
    def __init__(self, input_dim: int = 256, latent_dim: int = 512, num_latents: int = 128):
        if TORCH_AVAILABLE:
            super().__init__()
        self.num_latents = num_latents
        self.inferences = 0
        if TORCH_AVAILABLE:
            self.latents = nn.Parameter(torch.randn(1, num_latents, latent_dim))
            self.encode_ca = CrossAttention(input_dim, latent_dim)
            self.decode_ca = CrossAttention(latent_dim, input_dim) # Decode back to query array size

    def encode_decode(self, inputs: 'torch.Tensor', output_queries: 'torch.Tensor') -> PerceiverResult:
        if not TORCH_AVAILABLE:
            return PerceiverResult(False, error="PerceiverError: Torch unavailable")
        try:
            self.inferences += 1
            B = inputs.shape[0]
            batch_latents = self.latents.expand(B, -1, -1)
            
            # Encode inputs into fixed latents
            encoded = self.encode_ca.forward(inputs, batch_latents)
            
            # Decode latents to arbitrary query array
            decoded = self.decode_ca.forward(encoded, output_queries)
            
            return PerceiverResult(True, latent_representation=encoded, output_array=decoded)
        except Exception as e:
            return PerceiverResult(False, error=f"PerceiverError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniPerceiverIoEngine", "inferences": self.inferences,
                "latents": self.num_latents, "status": "Operational" if TORCH_AVAILABLE else "Disabled"}
