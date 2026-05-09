"""
omni_wav2vec2.py — Audio Representation Learning
Layer: Compute / AI

Implements the feature extraction and Transformer encoding logic for
Wav2Vec2, enabling speech recognition. Fully implemented, zero mocks.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniWav2Vec2FeatureExtractor(nn.Module):
    """
    1D Convolutional feature extractor to process raw audio waveforms
    into dense vector representations.
    """
    def __init__(self):
        super().__init__()
        
        # Typical Wav2Vec2 conv configuration:
        # [(512, 10, 5), (512, 3, 2), (512, 3, 2), (512, 3, 2), (512, 3, 2), (512, 2, 2), (512, 2, 2)]
        self.conv_layers = nn.ModuleList([
            nn.Conv1d(1, 512, kernel_size=10, stride=5, bias=False),
            nn.Conv1d(512, 512, kernel_size=3, stride=2, bias=False),
            nn.Conv1d(512, 512, kernel_size=3, stride=2, bias=False),
            nn.Conv1d(512, 512, kernel_size=3, stride=2, bias=False),
            nn.Conv1d(512, 512, kernel_size=3, stride=2, bias=False),
            nn.Conv1d(512, 512, kernel_size=2, stride=2, bias=False),
            nn.Conv1d(512, 512, kernel_size=2, stride=2, bias=False)
        ])
        
        self.layer_norms = nn.ModuleList([nn.GroupNorm(512, 512) for _ in range(7)])

    def forward(self, waveforms: torch.Tensor) -> torch.Tensor:
        """
        waveforms: (Batch, 1, Length)
        """
        x = waveforms
        for conv, norm in zip(self.conv_layers, self.layer_norms):
            x = F.gelu(norm(conv(x)))
        return x

class OmniWav2Vec2Encoder(nn.Module):
    """
    Transformer encoder operating on the latent speech representations.
    """
    def __init__(self, embed_dim: int = 768, num_layers: int = 12):
        super().__init__()
        
        self.feature_projection = nn.Linear(512, embed_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, 
            nhead=12, 
            dim_feedforward=3072, 
            batch_first=True, 
            activation="gelu"
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
    def forward(self, features: torch.Tensor, padding_mask: torch.Tensor = None) -> torch.Tensor:
        """
        features: (Batch, Channels, SeqLen)
        """
        # (Batch, SeqLen, Channels)
        x = features.transpose(1, 2)
        x = self.feature_projection(x)
        
        encoded = self.transformer(x, src_key_padding_mask=padding_mask)
        return encoded

class OmniAudioTranscriber(nn.Module):
    """
    Full pipeline for speech-to-text modeling.
    """
    def __init__(self, vocab_size: int = 32):
        super().__init__()
        self.extractor = OmniWav2Vec2FeatureExtractor()
        self.encoder = OmniWav2Vec2Encoder()
        self.lm_head = nn.Linear(768, vocab_size)
        
    def forward(self, waveforms: torch.Tensor) -> torch.Tensor:
        features = self.extractor(waveforms)
        encoded = self.encoder(features)
        logits = self.lm_head(encoded)
        return logits
