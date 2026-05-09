"""
moe_audio_conversion.py — Compute / Audio Processing
Layer: Compute / Media — Voice Conversion via MoE

Applies the Mixture-of-Experts architecture to audio processing (TTS and Voice Conversion).
Different experts specialize in different phonemes, accents, or vocal characteristics
(e.g., "kawaii", "deep", "robotic"). The router acts as a dynamic style mixer.
"""
import torch
import torch.nn as nn
from typing import Dict

class VocalExpert(nn.Module):
    """
    An expert specialized in generating a specific vocal timbre or style.
    Processes audio mel-spectrogram embeddings.
    """
    def __init__(self, emb_dim: int, hidden_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(emb_dim, hidden_dim, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv1d(hidden_dim, emb_dim, kernel_size=3, padding=1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x expected shape for Conv1d: (Batch, Channels, Length)
        return self.net(x)

class AudioMoERouter(nn.Module):
    """
    Routes the input text or base audio embedding to the appropriate vocal experts.
    """
    def __init__(self, emb_dim: int, num_experts: int):
        super().__init__()
        # We pool the temporal dimension to make a routing decision per utterance
        self.gate = nn.Linear(emb_dim, num_experts)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (Batch, Channels, Length)
        # Global average pooling over the time dimension
        pooled = x.mean(dim=-1) # (Batch, Channels)
        logits = self.gate(pooled) # (Batch, num_experts)
        return torch.softmax(logits, dim=-1)

class KawaiiVoiceMoE(nn.Module):
    """
    MoE dedicated to high-quality dynamic voice synthesis.
    """
    def __init__(self, emb_dim: int, hidden_dim: int, num_experts: int = 4):
        super().__init__()
        self.emb_dim = emb_dim
        self.num_experts = num_experts
        
        self.router = AudioMoERouter(emb_dim, num_experts)
        self.experts = nn.ModuleList([
            VocalExpert(emb_dim, hidden_dim) for _ in range(num_experts)
        ])

    def forward(self, mel_spectrogram: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        mel_spectrogram: (Batch, emb_dim, Length)
        """
        B, C, L = mel_spectrogram.shape
        
        # Get routing weights: (Batch, num_experts)
        routing_weights = self.router(mel_spectrogram)
        
        final_audio = torch.zeros_like(mel_spectrogram)
        
        # Process through all experts (Soft MoE approach for smooth voice blending)
        for i in range(self.num_experts):
            expert_out = self.experts[i](mel_spectrogram) # (B, C, L)
            
            # Broadcast weight over Channels and Length
            weight = routing_weights[:, i].view(B, 1, 1)
            
            final_audio += expert_out * weight
            
        return {
            "converted_audio": final_audio,
            "style_weights": routing_weights
        }
