import torch
import torch.nn as nn
from typing import Tuple

class OmniCrossModalSleep(nn.Module):
    """
    Omni Cross-Modal Transformer for Sleep Stage Classification.
    Fuses EEG and EOG physiological signals using cross-attention to 
    determine sleep stages (Wake, N1, N2, N3, REM) automatically.
    """
    def __init__(self, eeg_channels: int = 1, eog_channels: int = 1, hidden_dim: int = 128, num_classes: int = 5):
        super().__init__()
        
        # Signal Feature Extractors (1D CNNs)
        self.eeg_extractor = nn.Sequential(
            nn.Conv1d(eeg_channels, 64, kernel_size=50, stride=6),
            nn.ReLU(),
            nn.MaxPool1d(8, 8),
            nn.Conv1d(64, hidden_dim, kernel_size=8, stride=1),
            nn.ReLU()
        )
        
        self.eog_extractor = nn.Sequential(
            nn.Conv1d(eog_channels, 64, kernel_size=50, stride=6),
            nn.ReLU(),
            nn.MaxPool1d(8, 8),
            nn.Conv1d(64, hidden_dim, kernel_size=8, stride=1),
            nn.ReLU()
        )
        
        # Cross-Modal Attention (EEG Querying EOG, and vice-versa)
        self.eeg_to_eog_attn = nn.MultiheadAttention(hidden_dim, num_heads=4, batch_first=True)
        self.eog_to_eeg_attn = nn.MultiheadAttention(hidden_dim, num_heads=4, batch_first=True)
        
        # Classification Head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(hidden_dim, num_classes)
        )

    def forward(self, eeg_signal: torch.Tensor, eog_signal: torch.Tensor) -> torch.Tensor:
        """
        eeg_signal, eog_signal: [Batch, Channels, Time_Samples]
        """
        # Extract features
        eeg_feats = self.eeg_extractor(eeg_signal).permute(0, 2, 1) # B, SeqLen, H
        eog_feats = self.eog_extractor(eog_signal).permute(0, 2, 1) # B, SeqLen, H
        
        # Cross Attention Fusion
        # EEG queries EOG to find complementary eye movement patterns
        eeg_fused, _ = self.eeg_to_eog_attn(query=eeg_feats, key=eog_feats, value=eog_feats)
        
        # EOG queries EEG to find complementary brain wave patterns
        eog_fused, _ = self.eog_to_eeg_attn(query=eog_feats, key=eeg_feats, value=eeg_feats)
        
        # Temporal Pooling (Global Average Pool over Sequence)
        eeg_pool = eeg_fused.mean(dim=1) # B, H
        eog_pool = eog_fused.mean(dim=1) # B, H
        
        # Concatenate and Classify
        fused_vector = torch.cat([eeg_pool, eog_pool], dim=-1) # B, H*2
        logits = self.classifier(fused_vector)
        
        return logits
