import torch
import torch.nn as nn
import math

class OmniTimeSformer(nn.Module):
    """
    Omni Multivariate Time Series Forecasting Transformer.
    Utilizes temporal embeddings and multi-headed self-attention to forecast 
    complex multi-dimensional time series variables.
    """
    def __init__(self, num_features: int, seq_len: int, pred_len: int, hidden_dim: int = 128, num_layers: int = 4):
        super().__init__()
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.hidden_dim = hidden_dim
        
        self.value_embedding = nn.Linear(num_features, hidden_dim)
        
        # Positional Encoding (Time embeddings)
        self.positional_encoding = nn.Parameter(torch.zeros(1, seq_len, hidden_dim))
        self._init_pe()
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim, 
            nhead=8, 
            dim_feedforward=hidden_dim * 4, 
            dropout=0.1, 
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Project hidden state back to future predictions
        self.decoder_projection = nn.Linear(seq_len * hidden_dim, pred_len * num_features)
        self.num_features = num_features

    def _init_pe(self):
        pe = torch.zeros(self.seq_len, self.hidden_dim)
        position = torch.arange(0, self.seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, self.hidden_dim, 2).float() * (-math.log(10000.0) / self.hidden_dim))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.positional_encoding.data = pe.unsqueeze(0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: [Batch, seq_len, num_features] historical time series
        Returns: [Batch, pred_len, num_features] forecasted future
        """
        B, L, F = x.shape
        x_emb = self.value_embedding(x) + self.positional_encoding
        
        # Auto-regressive features mapped via self-attention
        memory = self.transformer_encoder(x_emb)
        
        # Flatten and decode
        memory_flat = memory.view(B, -1)
        out_flat = self.decoder_projection(memory_flat)
        
        out = out_flat.view(B, self.pred_len, self.num_features)
        return out
