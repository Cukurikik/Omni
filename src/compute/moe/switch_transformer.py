"""
switch_transformer.py — Switch Transformer Implementation
Reference: srishti-git1110/torch-switch-transformers, Google Switch Transformer paper
Layer: Compute / AI — MoE Architecture

Switch Transformers simplify MoE by routing each token to exactly one expert
(top-1), with capacity factor and auxiliary loss for load balancing.
This is the simplest and most efficient MoE routing strategy.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional
from dataclasses import dataclass
import math


@dataclass
class SwitchConfig:
    dim: int = 512
    num_experts: int = 8
    ff_dim: int = 2048
    capacity_factor: float = 1.0
    jitter_noise: float = 0.01
    dropout: float = 0.1
    load_balance_weight: float = 0.01
    num_heads: int = 8
    num_layers: int = 6
    vocab_size: int = 32000
    max_seq_len: int = 512


class SwitchExpert(nn.Module):
    """Standard FFN expert for Switch Transformer."""
    def __init__(self, dim, ff_dim, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, ff_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class SwitchRouter(nn.Module):
    """Top-1 router with jitter noise and capacity control.

    Each token is routed to exactly one expert. The capacity factor
    limits how many tokens each expert can process, preventing
    memory overflow from imbalanced routing.
    """
    def __init__(self, dim, num_experts, capacity_factor=1.0, jitter=0.01):
        super().__init__()
        self.classifier = nn.Linear(dim, num_experts, bias=False)
        self.num_experts = num_experts
        self.capacity_factor = capacity_factor
        self.jitter = jitter

    def forward(self, x):
        # x: (batch * seq, dim)
        if self.training and self.jitter > 0:
            x = x * (1.0 + self.jitter * (2 * torch.rand_like(x) - 1))

        logits = self.classifier(x)
        probs = F.softmax(logits, dim=-1)
        expert_idx = probs.argmax(dim=-1)  # top-1
        expert_weight = probs.gather(1, expert_idx.unsqueeze(-1)).squeeze(-1)

        return expert_weight, expert_idx, logits, probs


class SwitchMoELayer(nn.Module):
    """Switch Transformer MoE Layer: top-1 expert routing with capacity."""
    def __init__(self, config: SwitchConfig):
        super().__init__()
        self.config = config
        self.router = SwitchRouter(
            config.dim, config.num_experts,
            config.capacity_factor, config.jitter_noise)
        self.experts = nn.ModuleList([
            SwitchExpert(config.dim, config.ff_dim, config.dropout)
            for _ in range(config.num_experts)])
        self.norm = nn.LayerNorm(config.dim)

    def forward(self, x):
        B, S, D = x.shape
        residual = x
        x_flat = self.norm(x).reshape(-1, D)
        N = x_flat.shape[0]

        weights, indices, logits, probs = self.router(x_flat)
        output = torch.zeros_like(x_flat)

        # Expert capacity: max tokens per expert
        capacity = max(1, int(N / self.config.num_experts * self.config.capacity_factor))

        # Route tokens to experts
        expert_counts = torch.zeros(self.config.num_experts, dtype=torch.long, device=x.device)
        for i in range(N):
            e = indices[i].item()
            if expert_counts[e] < capacity:
                expert_out = self.experts[e](x_flat[i:i+1])
                output[i] = expert_out.squeeze(0) * weights[i]
                expert_counts[e] += 1
            # Dropped tokens get zero contribution (residual will carry them)

        output = output.reshape(B, S, D) + residual

        # Auxiliary load balance loss
        # f_i = fraction of tokens routed to expert i
        # p_i = mean router probability for expert i
        f = F.one_hot(indices, self.config.num_experts).float().mean(dim=0)
        p = probs.mean(dim=0)
        aux_loss = (f * p).sum() * self.config.num_experts

        return {
            "output": output,
            "aux_loss": aux_loss * self.config.load_balance_weight,
            "expert_counts": expert_counts,
            "dropped_tokens": max(0, N - expert_counts.sum().item()),
        }


class SwitchTransformerBlock(nn.Module):
    """Full transformer block with attention + Switch MoE FFN."""
    def __init__(self, config: SwitchConfig, use_moe: bool = True):
        super().__init__()
        self.attn_norm = nn.LayerNorm(config.dim)
        self.attn = nn.MultiheadAttention(
            config.dim, config.num_heads,
            dropout=config.dropout, batch_first=True)

        if use_moe:
            self.ffn = SwitchMoELayer(config)
            self.is_moe = True
        else:
            self.ffn_norm = nn.LayerNorm(config.dim)
            self.ffn = nn.Sequential(
                nn.Linear(config.dim, config.ff_dim),
                nn.ReLU(),
                nn.Dropout(config.dropout),
                nn.Linear(config.ff_dim, config.dim),
                nn.Dropout(config.dropout))
            self.is_moe = False

    def forward(self, x, mask=None):
        normed = self.attn_norm(x)
        attn_out, _ = self.attn(normed, normed, normed, key_padding_mask=mask)
        x = x + attn_out

        if self.is_moe:
            result = self.ffn(x)
            return result
        else:
            x = x + self.ffn(self.ffn_norm(x))
            return {"output": x, "aux_loss": torch.tensor(0.0, device=x.device)}


class SwitchTransformerModel(nn.Module):
    """Full Switch Transformer: alternates dense and MoE layers."""
    def __init__(self, config: SwitchConfig):
        super().__init__()
        self.config = config
        self.embed = nn.Embedding(config.vocab_size, config.dim)
        self.pos_embed = nn.Embedding(config.max_seq_len, config.dim)

        # Every other layer uses MoE (Switch paper pattern)
        self.layers = nn.ModuleList([
            SwitchTransformerBlock(config, use_moe=(i % 2 == 1))
            for i in range(config.num_layers)])
        self.final_norm = nn.LayerNorm(config.dim)
        self.lm_head = nn.Linear(config.dim, config.vocab_size, bias=False)

    def forward(self, input_ids):
        B, S = input_ids.shape
        positions = torch.arange(S, device=input_ids.device).unsqueeze(0)
        x = self.embed(input_ids) + self.pos_embed(positions)
        total_aux = torch.tensor(0.0, device=x.device)

        for layer in self.layers:
            result = layer(x)
            x = result["output"]
            total_aux = total_aux + result["aux_loss"]

        logits = self.lm_head(self.final_norm(x))
        return {"logits": logits, "aux_loss": total_aux}
