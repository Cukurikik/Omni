"""
hydra_mqa_moe.py — HydraNet-style MQA + MoE Transformer
Reference: Agora-Lab-AI/HydraNet, kyegomez/Mixture-of-MQA
Layer: Compute / AI — MoE Architecture

Multi-Query Attention combined with Mixture of Experts FFN.
MQA shares K/V heads across query heads for memory efficiency,
while MoE replaces dense FFN with sparse expert routing.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass
from typing import Optional, Tuple, Dict
import math


@dataclass
class HydraMoEConfig:
    dim: int = 768
    num_heads: int = 12
    num_kv_heads: int = 1  # MQA: single KV head
    num_experts: int = 8
    top_k: int = 2
    ff_mult: float = 4.0
    dropout: float = 0.0
    max_seq_len: int = 2048
    rope_base: float = 10000.0
    load_balance_coeff: float = 0.01
    capacity_factor: float = 1.25


class RotaryEmbedding(nn.Module):
    """RoPE positional encoding for transformer attention."""
    def __init__(self, dim, max_seq_len=2048, base=10000.0):
        super().__init__()
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self._build_cache(max_seq_len)

    def _build_cache(self, seq_len):
        t = torch.arange(seq_len, device=self.inv_freq.device).float()
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        self.register_buffer("cos_cached", emb.cos().unsqueeze(0).unsqueeze(0))
        self.register_buffer("sin_cached", emb.sin().unsqueeze(0).unsqueeze(0))

    def forward(self, x, seq_len):
        if seq_len > self.cos_cached.shape[2]:
            self._build_cache(seq_len)
        return self.cos_cached[:, :, :seq_len], self.sin_cached[:, :, :seq_len]


def rotate_half(x):
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat([-x2, x1], dim=-1)


def apply_rope(q, k, cos, sin):
    q = q * cos + rotate_half(q) * sin
    k = k * cos + rotate_half(k) * sin
    return q, k


class MultiQueryAttention(nn.Module):
    """Multi-Query Attention: shares KV across all query heads."""
    def __init__(self, config: HydraMoEConfig):
        super().__init__()
        self.num_heads = config.num_heads
        self.num_kv_heads = config.num_kv_heads
        self.head_dim = config.dim // config.num_heads
        self.kv_groups = config.num_heads // config.num_kv_heads

        self.q_proj = nn.Linear(config.dim, config.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(config.dim, config.num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(config.dim, config.num_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(config.num_heads * self.head_dim, config.dim, bias=False)
        self.rope = RotaryEmbedding(self.head_dim, config.max_seq_len, config.rope_base)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x, mask=None):
        B, S, _ = x.shape
        q = self.q_proj(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, S, self.num_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, S, self.num_kv_heads, self.head_dim).transpose(1, 2)

        cos, sin = self.rope(q, S)
        q, k = apply_rope(q, k, cos, sin)

        # Repeat KV heads for grouped attention
        if self.kv_groups > 1:
            k = k.repeat_interleave(self.kv_groups, dim=1)
            v = v.repeat_interleave(self.kv_groups, dim=1)

        scale = 1.0 / math.sqrt(self.head_dim)
        attn = torch.matmul(q, k.transpose(-2, -1)) * scale

        if mask is not None:
            attn = attn.masked_fill(mask == 0, float("-inf"))

        # Causal mask
        causal = torch.triu(torch.ones(S, S, device=x.device, dtype=torch.bool), diagonal=1)
        attn = attn.masked_fill(causal.unsqueeze(0).unsqueeze(0), float("-inf"))

        attn = self.dropout(F.softmax(attn, dim=-1))
        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).contiguous().view(B, S, -1)
        return self.o_proj(out)


class SwiGLUExpert(nn.Module):
    """Single expert using SwiGLU activation."""
    def __init__(self, dim, ff_dim, dropout=0.0):
        super().__init__()
        self.w1 = nn.Linear(dim, ff_dim, bias=False)
        self.w2 = nn.Linear(ff_dim, dim, bias=False)
        self.w3 = nn.Linear(dim, ff_dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.dropout(self.w2(F.silu(self.w1(x)) * self.w3(x)))


class HydraRouter(nn.Module):
    """Router with noisy top-k gating and z-loss stabilization."""
    def __init__(self, dim, num_experts, top_k=2, noise_std=0.1):
        super().__init__()
        self.gate = nn.Linear(dim, num_experts, bias=False)
        self.top_k = top_k
        self.noise_std = noise_std
        self.num_experts = num_experts

    def forward(self, x):
        logits = self.gate(x)
        if self.training and self.noise_std > 0:
            logits = logits + torch.randn_like(logits) * self.noise_std
        topk_vals, topk_idx = torch.topk(logits, self.top_k, dim=-1)
        topk_weights = F.softmax(topk_vals, dim=-1)
        # Z-loss: penalize large router logits for stability
        z_loss = (torch.logsumexp(logits, dim=-1) ** 2).mean()
        return topk_weights, topk_idx, logits, z_loss


class HydraMoEBlock(nn.Module):
    """Transformer block combining MQA + sparse MoE FFN."""
    def __init__(self, config: HydraMoEConfig):
        super().__init__()
        self.config = config
        ff_dim = int(config.dim * config.ff_mult)

        self.attn_norm = nn.RMSNorm(config.dim)
        self.ffn_norm = nn.RMSNorm(config.dim)
        self.attn = MultiQueryAttention(config)
        self.router = HydraRouter(config.dim, config.num_experts, config.top_k)
        self.experts = nn.ModuleList([
            SwiGLUExpert(config.dim, ff_dim, config.dropout)
            for _ in range(config.num_experts)])

    def forward(self, x, mask=None):
        B, S, D = x.shape
        # Attention with pre-norm residual
        x = x + self.attn(self.attn_norm(x), mask)

        # MoE FFN
        residual = x
        normed = self.ffn_norm(x).reshape(-1, D)
        N = normed.shape[0]

        weights, indices, logits, z_loss = self.router(normed)
        output = torch.zeros_like(normed)

        for e_idx in range(self.config.num_experts):
            mask_e = (indices == e_idx).any(dim=-1)
            if not mask_e.any():
                continue
            tok_idx = mask_e.nonzero(as_tuple=True)[0]
            cap = int(N * self.config.capacity_factor / self.config.num_experts)
            tok_idx = tok_idx[:cap]
            e_out = self.experts[e_idx](normed[tok_idx])
            for k in range(self.config.top_k):
                km = indices[tok_idx, k] == e_idx
                if km.any():
                    ki = tok_idx[km]
                    output[ki] += e_out[km] * weights[ki, k].unsqueeze(-1)

        output = output.reshape(B, S, D) + residual

        # Load balance loss
        probs = F.softmax(logits, dim=-1)
        expert_frac = F.one_hot(indices[:, 0], self.config.num_experts).float().mean(0)
        prob_mean = probs.mean(0)
        lb_loss = (expert_frac * prob_mean).sum() * self.config.num_experts

        return {
            "output": output,
            "load_balance_loss": lb_loss * self.config.load_balance_coeff,
            "z_loss": z_loss * 1e-4,
        }


class HydraMoEModel(nn.Module):
    """Full HydraNet-style MQA + MoE model."""
    def __init__(self, config: HydraMoEConfig, num_layers: int = 12,
                 vocab_size: int = 32000):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, config.dim)
        self.layers = nn.ModuleList([HydraMoEBlock(config) for _ in range(num_layers)])
        self.norm = nn.RMSNorm(config.dim)
        self.lm_head = nn.Linear(config.dim, vocab_size, bias=False)
        self.embed.weight = self.lm_head.weight  # weight tying

    def forward(self, input_ids, mask=None):
        x = self.embed(input_ids)
        total_lb = torch.tensor(0.0, device=x.device)
        total_z = torch.tensor(0.0, device=x.device)
        for layer in self.layers:
            result = layer(x, mask)
            x = result["output"]
            total_lb = total_lb + result["load_balance_loss"]
            total_z = total_z + result["z_loss"]
        logits = self.lm_head(self.norm(x))
        return {"logits": logits, "aux_loss": total_lb + total_z}
