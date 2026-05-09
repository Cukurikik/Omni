"""
OMNI Transformer — Graph Transformer
Attention mechanism on graph-structured data.
Learned from: graphormer, molecular transformer patterns
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class GraphTransformerConfig:
    node_dim: int = 128
    edge_dim: int = 64
    embed_dim: int = 256
    num_layers: int = 6
    num_heads: int = 8
    ffn_dim: int = 1024
    max_nodes: int = 512
    dropout: float = 0.1
    num_classes: int = 10


class GraphAttention(nn.Module):
    """Graph multi-head attention with edge features."""
    def __init__(self, embed_dim: int, num_heads: int, edge_dim: int = 0, dropout: float = 0.0):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5

        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.o_proj = nn.Linear(embed_dim, embed_dim)

        if edge_dim > 0:
            self.edge_proj = nn.Linear(edge_dim, num_heads)
        else:
            self.edge_proj = None

        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, edge_features: Optional[torch.Tensor] = None,
                adjacency_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, N, D = x.shape
        H = self.num_heads

        q = self.q_proj(x).view(B, N, H, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, N, H, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, N, H, self.head_dim).transpose(1, 2)

        attn = (q @ k.transpose(-2, -1)) * self.scale

        # Add edge bias
        if self.edge_proj is not None and edge_features is not None:
            edge_bias = self.edge_proj(edge_features).permute(0, 3, 1, 2)
            attn = attn + edge_bias

        # Apply adjacency mask
        if adjacency_mask is not None:
            attn = attn.masked_fill(~adjacency_mask.unsqueeze(1).bool(), float("-inf"))

        attn = self.dropout(F.softmax(attn, dim=-1))
        out = (attn @ v).transpose(1, 2).contiguous().view(B, N, D)
        return self.o_proj(out)


class GraphTransformerBlock(nn.Module):
    def __init__(self, config: GraphTransformerConfig):
        super().__init__()
        self.norm1 = nn.LayerNorm(config.embed_dim)
        self.attn = GraphAttention(config.embed_dim, config.num_heads, config.edge_dim, config.dropout)
        self.norm2 = nn.LayerNorm(config.embed_dim)
        self.ffn = nn.Sequential(
            nn.Linear(config.embed_dim, config.ffn_dim), nn.GELU(),
            nn.Dropout(config.dropout), nn.Linear(config.ffn_dim, config.embed_dim),
        )

    def forward(self, x: torch.Tensor, edge_features: Optional[torch.Tensor] = None,
                adjacency_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = x + self.attn(self.norm1(x), edge_features, adjacency_mask)
        x = x + self.ffn(self.norm2(x))
        return x


class OmniGraphTransformer(nn.Module):
    """Production graph transformer for node/graph classification."""
    def __init__(self, config: GraphTransformerConfig):
        super().__init__()
        self.node_embed = nn.Linear(config.node_dim, config.embed_dim)
        self.layers = nn.ModuleList([GraphTransformerBlock(config) for _ in range(config.num_layers)])
        self.norm = nn.LayerNorm(config.embed_dim)
        self.classifier = nn.Linear(config.embed_dim, config.num_classes)

    def forward(self, node_features: torch.Tensor, edge_features: Optional[torch.Tensor] = None,
                adjacency_mask: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None) -> Dict:
        x = self.node_embed(node_features)
        for layer in self.layers:
            x = layer(x, edge_features, adjacency_mask)
        x = self.norm(x)
        pooled = x.mean(dim=1)
        logits = self.classifier(pooled)
        loss = F.cross_entropy(logits, labels) if labels is not None else None
        return {"logits": logits, "loss": loss, "node_embeddings": x}
