import torch
import torch.nn as nn
from typing import Tuple, Optional

class OmniPonderTransformerLayer(nn.Module):
    def __init__(self, dim: int, heads: int, dim_head: int = 64, dropout: float = 0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * 4, dim),
            nn.Dropout(dropout)
        )
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        res = x
        x = self.norm1(x)
        x, _ = self.attn(x, x, x, key_padding_mask=mask)
        x = x + res
        
        res = x
        x = self.norm2(x)
        x = self.ffn(x)
        x = x + res
        return x

class OmniPonderTransformer(nn.Module):
    """
    Omni Ponder Transformer Network
    Implements Adaptive Computation Time (ACT) allowing the model to dynamically 
    determine the number of compute steps per token. Inspired by PonderNet.
    """
    def __init__(self, vocab_size: int, dim: int = 512, max_steps: int = 10, threshold: float = 0.99):
        super().__init__()
        self.dim = dim
        self.max_steps = max_steps
        self.threshold = threshold
        
        self.embedding = nn.Embedding(vocab_size, dim)
        self.layer = OmniPonderTransformerLayer(dim, heads=8)
        
        # ACT Halting predictor
        self.halt_proj = nn.Sequential(
            nn.Linear(dim, dim // 2),
            nn.ReLU(),
            nn.Linear(dim // 2, 1),
            nn.Sigmoid()
        )
        self.to_out = nn.Linear(dim, vocab_size)

    def forward(self, x: torch.Tensor, pad_mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        B, N = x.shape
        x = self.embedding(x)
        
        halting_probabilities = torch.zeros(B, N, device=x.device)
        remainders = torch.ones(B, N, device=x.device)
        updates = torch.zeros(B, N, self.dim, device=x.device)
        steps_taken = torch.zeros(B, N, device=x.device)
        
        for step in range(self.max_steps):
            x = self.layer(x, mask=pad_mask)
            
            p = self.halt_proj(x).squeeze(-1)
            
            # Ensure p=1 on the last step
            if step == self.max_steps - 1:
                p = torch.ones_like(p)
                
            # Calculate act probabilities
            p_actual = p * remainders
            remainders = remainders - p_actual
            
            # Accumulate
            updates = updates + p_actual.unsqueeze(-1) * x
            halting_probabilities = halting_probabilities + p_actual
            steps_taken = steps_taken + remainders.gt(0).float()
            
            # Stop early if all sequences reached the threshold
            if (1 - remainders).min() >= self.threshold:
                break
                
        out = self.to_out(updates)
        return out, steps_taken, halting_probabilities
