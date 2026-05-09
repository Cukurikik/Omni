"""
OMNI Transformer — Embedding Models
Production sentence/document embedding using pooling strategies.
Learned from: Bangla-RAG/PoRAG, sentence-transformers
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List
from ..core import TransformerEncoderBlock, AttentionType, NormType, FFNActivation


class EmbeddingPooler(nn.Module):
    """Pooling strategies for sequence embeddings."""
    def __init__(self, strategy: str = "mean"):
        super().__init__()
        self.strategy = strategy

    def forward(self, hidden: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        if self.strategy == "cls":
            return hidden[:, 0]
        elif self.strategy == "mean":
            if mask is not None:
                mask_expanded = mask.unsqueeze(-1).float()
                return (hidden * mask_expanded).sum(1) / mask_expanded.sum(1).clamp(min=1e-9)
            return hidden.mean(dim=1)
        elif self.strategy == "max":
            if mask is not None:
                hidden = hidden.masked_fill(~mask.unsqueeze(-1).bool(), float("-inf"))
            return hidden.max(dim=1).values
        return hidden[:, 0]


class OmniEmbeddingModel(nn.Module):
    """Production embedding model for semantic search and RAG."""
    def __init__(self, vocab_size: int = 30522, embed_dim: int = 768, num_layers: int = 6,
                 num_heads: int = 12, ffn_dim: int = 3072, max_seq_len: int = 512,
                 pooling: str = "mean", normalize: bool = True):
        super().__init__()
        self.normalize = normalize
        self.word_embed = nn.Embedding(vocab_size, embed_dim)
        self.pos_embed = nn.Embedding(max_seq_len, embed_dim)
        self.layers = nn.ModuleList([
            TransformerEncoderBlock(embed_dim=embed_dim, num_heads=num_heads, ffn_dim=ffn_dim,
                                   dropout=0.1, activation=FFNActivation.GELU,
                                   norm_type=NormType.LAYER_NORM, attention_type=AttentionType.STANDARD,
                                   use_rope=False)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(embed_dim)
        self.pooler = EmbeddingPooler(pooling)

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, S = input_ids.shape
        pos = torch.arange(S, device=input_ids.device).unsqueeze(0)
        hidden = self.word_embed(input_ids) + self.pos_embed(pos)
        mask = None
        if attention_mask is not None:
            mask = (1.0 - attention_mask.unsqueeze(1).unsqueeze(2).float()) * -1e9
        for layer in self.layers:
            hidden = layer(hidden, attention_mask=mask)
        hidden = self.norm(hidden)
        embeddings = self.pooler(hidden, attention_mask)
        if self.normalize:
            embeddings = F.normalize(embeddings, p=2, dim=-1)
        return embeddings
