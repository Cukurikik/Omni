"""
vision_language_moe.py — Vision-Language MoE for Multi-Modal Understanding
Reference: CongcongWen1208/RS-MoE (IEEE TGRS 2025)
Layer: Compute / AI — Multi-Modal MoE

MoE architecture for vision-language tasks. Uses modality-aware expert
routing where visual and textual tokens are directed to specialized
experts. Implements cross-modal attention with MoE FFN layers.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class VLMoEConfig:
    vision_dim: int = 768
    text_dim: int = 768
    hidden_dim: int = 768
    num_experts: int = 8
    num_vision_experts: int = 3
    num_text_experts: int = 3
    num_shared_experts: int = 2
    top_k: int = 2
    num_heads: int = 12
    ff_mult: float = 4.0
    dropout: float = 0.1
    max_visual_tokens: int = 256
    max_text_tokens: int = 512


class ModalityAwareRouter(nn.Module):
    """Routes tokens to modality-specific or shared experts.

    Expert layout: [vision_experts | text_experts | shared_experts]
    Visual tokens are biased toward vision experts, text tokens toward
    text experts, but can still access shared experts.
    """
    def __init__(self, dim, config: VLMoEConfig):
        super().__init__()
        total = config.num_vision_experts + config.num_text_experts + config.num_shared_experts
        self.gate = nn.Linear(dim, total, bias=False)
        self.top_k = config.top_k
        self.n_vis = config.num_vision_experts
        self.n_txt = config.num_text_experts
        self.n_shared = config.num_shared_experts
        self.total = total

        # Learnable modality bias
        self.vision_bias = nn.Parameter(torch.zeros(total))
        self.text_bias = nn.Parameter(torch.zeros(total))

        # Initialize biases to prefer modality-specific experts
        with torch.no_grad():
            self.vision_bias[:self.n_vis] = 1.0
            self.vision_bias[self.n_vis:self.n_vis+self.n_txt] = -1.0
            self.text_bias[:self.n_vis] = -1.0
            self.text_bias[self.n_vis:self.n_vis+self.n_txt] = 1.0

    def forward(self, x, modality_mask=None):
        """Route tokens with modality-aware bias.

        Args:
            x: (N, D) tokens
            modality_mask: (N,) 0=vision, 1=text
        """
        logits = self.gate(x)
        if modality_mask is not None:
            vis_mask = (modality_mask == 0).float().unsqueeze(-1)
            txt_mask = (modality_mask == 1).float().unsqueeze(-1)
            logits = logits + vis_mask * self.vision_bias + txt_mask * self.text_bias

        topk_val, topk_idx = torch.topk(logits, self.top_k, dim=-1)
        topk_w = F.softmax(topk_val, dim=-1)
        return topk_w, topk_idx, logits


class VisionProjector(nn.Module):
    """Projects vision features to the shared hidden dimension."""
    def __init__(self, vision_dim, hidden_dim):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(vision_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, x):
        return self.norm(self.proj(x))


class CrossModalAttention(nn.Module):
    """Cross-attention between vision and language tokens."""
    def __init__(self, dim, num_heads, dropout=0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.norm_q = nn.LayerNorm(dim)
        self.norm_kv = nn.LayerNorm(dim)

    def forward(self, query, context, mask=None):
        q = self.norm_q(query)
        kv = self.norm_kv(context)
        out, _ = self.attn(q, kv, kv, key_padding_mask=mask)
        return query + out


class MoEFFNLayer(nn.Module):
    """MoE Feed-Forward layer with modality-aware routing."""
    def __init__(self, config: VLMoEConfig):
        super().__init__()
        ff_dim = int(config.hidden_dim * config.ff_mult)
        total_experts = config.num_vision_experts + config.num_text_experts + config.num_shared_experts

        self.router = ModalityAwareRouter(config.hidden_dim, config)
        self.experts = nn.ModuleList()
        for _ in range(total_experts):
            self.experts.append(nn.Sequential(
                nn.Linear(config.hidden_dim, ff_dim),
                nn.GELU(),
                nn.Dropout(config.dropout),
                nn.Linear(ff_dim, config.hidden_dim),
                nn.Dropout(config.dropout),
            ))
        self.norm = nn.LayerNorm(config.hidden_dim)
        self.num_experts = total_experts
        self.top_k = config.top_k

    def forward(self, x, modality_mask=None):
        residual = x
        B, S, D = x.shape
        flat = self.norm(x).reshape(-1, D)
        mod_flat = modality_mask.reshape(-1) if modality_mask is not None else None

        weights, indices, logits = self.router(flat, mod_flat)
        output = torch.zeros_like(flat)

        for e in range(self.num_experts):
            mask = (indices == e).any(dim=-1)
            if not mask.any():
                continue
            tok_idx = mask.nonzero(as_tuple=True)[0]
            e_out = self.experts[e](flat[tok_idx])
            for k in range(self.top_k):
                km = indices[tok_idx, k] == e
                if km.any():
                    ki = tok_idx[km]
                    output[ki] += e_out[km] * weights[ki, k].unsqueeze(-1)

        output = output.reshape(B, S, D) + residual

        # Load balance loss
        probs = F.softmax(logits, dim=-1)
        frac = F.one_hot(indices[:, 0], self.num_experts).float().mean(0)
        lb_loss = (frac * probs.mean(0)).sum() * self.num_experts
        return output, lb_loss


class VisionLanguageMoEBlock(nn.Module):
    """Single VL-MoE transformer block."""
    def __init__(self, config: VLMoEConfig):
        super().__init__()
        self.self_attn_norm = nn.LayerNorm(config.hidden_dim)
        self.self_attn = nn.MultiheadAttention(
            config.hidden_dim, config.num_heads,
            dropout=config.dropout, batch_first=True)
        self.cross_attn = CrossModalAttention(
            config.hidden_dim, config.num_heads, config.dropout)
        self.moe_ffn = MoEFFNLayer(config)

    def forward(self, x, context=None, modality_mask=None):
        # Self-attention
        normed = self.self_attn_norm(x)
        sa_out, _ = self.self_attn(normed, normed, normed)
        x = x + sa_out

        # Cross-modal attention (if context available)
        if context is not None:
            x = self.cross_attn(x, context)

        # MoE FFN
        x, lb_loss = self.moe_ffn(x, modality_mask)
        return x, lb_loss


class VisionLanguageMoE(nn.Module):
    """Complete Vision-Language MoE model."""
    def __init__(self, config: VLMoEConfig, num_layers: int = 6,
                 vocab_size: int = 32000):
        super().__init__()
        self.config = config
        self.vision_proj = VisionProjector(config.vision_dim, config.hidden_dim)
        self.text_embed = nn.Embedding(vocab_size, config.text_dim)
        self.text_proj = nn.Linear(config.text_dim, config.hidden_dim) \
            if config.text_dim != config.hidden_dim else nn.Identity()

        self.layers = nn.ModuleList([
            VisionLanguageMoEBlock(config) for _ in range(num_layers)])
        self.norm = nn.LayerNorm(config.hidden_dim)
        self.lm_head = nn.Linear(config.hidden_dim, vocab_size, bias=False)

    def forward(self, vision_features, text_ids):
        vis_tokens = self.vision_proj(vision_features)
        txt_tokens = self.text_proj(self.text_embed(text_ids))

        B = vis_tokens.shape[0]
        V = vis_tokens.shape[1]
        T = txt_tokens.shape[1]
        x = torch.cat([vis_tokens, txt_tokens], dim=1)

        mod_mask = torch.cat([
            torch.zeros(B, V, device=x.device, dtype=torch.long),
            torch.ones(B, T, device=x.device, dtype=torch.long)], dim=1)

        total_lb = torch.tensor(0.0, device=x.device)
        for layer in self.layers:
            x, lb = layer(x, modality_mask=mod_mask)
            total_lb = total_lb + lb

        text_out = x[:, V:]
        logits = self.lm_head(self.norm(text_out))
        return {"logits": logits, "aux_loss": total_lb * 0.01}
