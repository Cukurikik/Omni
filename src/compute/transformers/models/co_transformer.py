"""
OMNI Transformer — Combinatorial Optimization Transformer
Solving routing/scheduling problems with attention mechanisms.
Learned from: ai4co/parco (NeurIPS 2024), rl4co
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class COConfig:
    input_dim: int = 2  # x,y coordinates for TSP
    embed_dim: int = 128
    num_layers: int = 6
    num_heads: int = 8
    ffn_dim: int = 512
    max_nodes: int = 200
    dropout: float = 0.0


class COEncoder(nn.Module):
    """Encoder for combinatorial optimization problems."""
    def __init__(self, config: COConfig):
        super().__init__()
        self.input_proj = nn.Linear(config.input_dim, config.embed_dim)
        self.layers = nn.ModuleList()
        for _ in range(config.num_layers):
            self.layers.append(nn.ModuleDict({
                "norm1": nn.LayerNorm(config.embed_dim),
                "attn": nn.MultiheadAttention(config.embed_dim, config.num_heads, batch_first=True),
                "norm2": nn.LayerNorm(config.embed_dim),
                "ffn": nn.Sequential(
                    nn.Linear(config.embed_dim, config.ffn_dim),
                    nn.ReLU(),
                    nn.Linear(config.ffn_dim, config.embed_dim),
                ),
            }))

    def forward(self, coordinates: torch.Tensor) -> torch.Tensor:
        x = self.input_proj(coordinates)
        for layer in self.layers:
            residual = x
            x = layer["norm1"](x)
            x, _ = layer["attn"](x, x, x)
            x = x + residual
            residual = x
            x = layer["norm2"](x)
            x = layer["ffn"](x) + residual
        return x


class AutoregressiveDecoder(nn.Module):
    """Autoregressive decoder for sequential decision making (e.g., TSP tour)."""
    def __init__(self, config: COConfig):
        super().__init__()
        self.embed_dim = config.embed_dim
        self.context_proj = nn.Linear(3 * config.embed_dim, config.embed_dim)
        self.query_proj = nn.Linear(config.embed_dim, config.embed_dim)
        self.key_proj = nn.Linear(config.embed_dim, config.embed_dim)
        self.scale = config.embed_dim ** -0.5
        self.logit_clipping = 10.0

    def forward(self, encoder_out: torch.Tensor, visited_mask: torch.Tensor,
                first_node: torch.Tensor, last_node: torch.Tensor) -> torch.Tensor:
        B, N, D = encoder_out.shape
        # Context: [graph_embedding, first_node_embed, last_node_embed]
        graph_emb = encoder_out.mean(dim=1)
        first_emb = torch.gather(encoder_out, 1, first_node.unsqueeze(-1).expand(-1, -1, D)).squeeze(1)
        last_emb = torch.gather(encoder_out, 1, last_node.unsqueeze(-1).expand(-1, -1, D)).squeeze(1)
        context = self.context_proj(torch.cat([graph_emb, first_emb, last_emb], dim=-1))

        query = self.query_proj(context).unsqueeze(1)
        keys = self.key_proj(encoder_out)
        logits = (query @ keys.transpose(-2, -1)) * self.scale
        logits = self.logit_clipping * torch.tanh(logits)
        logits = logits.squeeze(1)

        # Mask visited nodes
        logits = logits.masked_fill(visited_mask.bool(), float("-inf"))
        return logits


class OmniCOSolver(nn.Module):
    """Production CO Transformer for TSP and routing problems."""
    def __init__(self, config: COConfig):
        super().__init__()
        self.encoder = COEncoder(config)
        self.decoder = AutoregressiveDecoder(config)

    def forward(self, coordinates: torch.Tensor, greedy: bool = False) -> Dict:
        B, N, _ = coordinates.shape
        encoder_out = self.encoder(coordinates)

        # Build tour autoregressively
        visited = torch.zeros(B, N, device=coordinates.device)
        tours = []
        log_probs = []

        # Start from node 0
        current = torch.zeros(B, 1, dtype=torch.long, device=coordinates.device)
        first = current.clone()
        visited.scatter_(1, current, 1.0)
        tours.append(current.squeeze(1))

        for step in range(N - 1):
            logits = self.decoder(encoder_out, visited, first.squeeze(1), current.squeeze(1))
            probs = F.softmax(logits, dim=-1)

            if greedy:
                next_node = probs.argmax(dim=-1, keepdim=True)
            else:
                next_node = torch.multinomial(probs, 1)

            log_prob = torch.log(torch.gather(probs, 1, next_node) + 1e-8)
            log_probs.append(log_prob.squeeze(1))
            visited.scatter_(1, next_node, 1.0)
            current = next_node
            tours.append(next_node.squeeze(1))

        tours = torch.stack(tours, dim=1)
        total_log_prob = torch.stack(log_probs, dim=1).sum(dim=1)

        # Compute tour length
        tour_coords = torch.gather(coordinates, 1, tours.unsqueeze(-1).expand(-1, -1, 2))
        diffs = tour_coords[:, 1:] - tour_coords[:, :-1]
        tour_length = diffs.norm(dim=-1).sum(dim=-1)
        # Add return to start
        tour_length += (tour_coords[:, -1] - tour_coords[:, 0]).norm(dim=-1)

        return {"tours": tours, "tour_length": tour_length, "log_prob": total_log_prob}
