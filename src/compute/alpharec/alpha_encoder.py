import torch
import torch.nn as nn

class AlphaRecEncoder(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.encoder = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=8)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(x)
        return self.encoder(embedded)
