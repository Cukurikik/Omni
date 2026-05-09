"""
omni_rq_transformer.py — Residual Quantization Transformer
Inspired by: lucidrains/RQ-Transformer
Layer: Compute / AI

Implements the RQ-Transformer which uses a spatial transformer and
a depth transformer to autoregressively model residual-quantized codes,
enabling high-fidelity image/audio generation.
"""

import torch
import torch.nn.functional as F
from torch import nn, einsum
from einops import rearrange, reduce, repeat
from typing import Optional, List


def exists(val):
    return val is not None


def remainder_to_mult(num: int, mult: int) -> int:
    return (mult - num % mult) % mult


def log(t: torch.Tensor, eps: float = 1e-20) -> torch.Tensor:
    return torch.log(t.clamp(min=eps))


def gumbel_noise(t: torch.Tensor) -> torch.Tensor:
    noise = torch.zeros_like(t).uniform_(0, 1)
    return -log(-log(noise))


def gumbel_sample(t: torch.Tensor, temperature: float = 1.0, dim: int = -1) -> torch.Tensor:
    return ((t / max(temperature, 1e-10)) + gumbel_noise(t)).argmax(dim=dim)


def top_k_filtering(logits: torch.Tensor, thres: float = 0.5) -> torch.Tensor:
    num_logits = logits.shape[-1]
    k = max(int((1 - thres) * num_logits), 1)
    val, ind = torch.topk(logits, k)
    probs = torch.full_like(logits, float('-inf'))
    probs.scatter_(-1, ind, val)
    return probs


class RQFeedForward(nn.Module):
    def __init__(self, dim: int, mult: int = 4, dropout: float = 0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim * mult),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * mult, dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class RQAttention(nn.Module):
    def __init__(self, dim: int, dim_head: int = 64, heads: int = 8,
                 dropout: float = 0.0, causal: bool = True):
        super().__init__()
        self.scale = dim_head ** -0.5
        self.heads = heads
        self.causal = causal
        inner_dim = dim_head * heads

        self.norm = nn.LayerNorm(dim)
        self.dropout = nn.Dropout(dropout)
        self.to_qkv = nn.Linear(dim, inner_dim * 3, bias=False)
        self.to_out = nn.Linear(inner_dim, dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h, device = self.heads, x.device
        x = self.norm(x)
        q, k, v = self.to_qkv(x).chunk(3, dim=-1)
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h=h), (q, k, v))

        q = q * self.scale
        sim = einsum('b h i d, b h j d -> b h i j', q, k)

        if self.causal:
            i, j = sim.shape[-2:]
            mask = torch.ones(i, j, dtype=torch.bool, device=device).triu(j - i + 1)
            sim = sim.masked_fill(mask, -torch.finfo(sim.dtype).max)

        sim = sim - sim.amax(dim=-1, keepdim=True).detach()
        attn = sim.softmax(dim=-1)
        attn = self.dropout(attn)

        out = einsum('b h i j, b h j d -> b h i d', attn, v)
        out = rearrange(out, 'b h n d -> b n (h d)')
        return self.to_out(out)


class RQTransformerBlock(nn.Module):
    def __init__(self, dim: int, dim_head: int = 64, heads: int = 8,
                 ff_mult: int = 4, attn_dropout: float = 0.0,
                 ff_dropout: float = 0.0):
        super().__init__()
        self.layers = nn.ModuleList([])
        self.attn = RQAttention(dim, dim_head, heads, attn_dropout)
        self.ff = RQFeedForward(dim, ff_mult, ff_dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.attn(x) + x
        x = self.ff(x) + x
        return x


class RQTransformerStack(nn.Module):
    def __init__(self, dim: int, layers: int, dim_head: int = 64,
                 heads: int = 8, ff_mult: int = 4,
                 attn_dropout: float = 0.0, ff_dropout: float = 0.0):
        super().__init__()
        self.blocks = nn.ModuleList([
            RQTransformerBlock(dim, dim_head, heads, ff_mult, attn_dropout, ff_dropout)
            for _ in range(layers)
        ])
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for block in self.blocks:
            x = block(x)
        return self.norm(x)


class OmniRQTransformer(nn.Module):
    """Residual Quantization Transformer for hierarchical discrete code generation.

    Decomposes the generation problem into:
    1. Spatial Transformer: models inter-position dependencies
    2. Depth Transformer: models residual quantization levels at each position

    This enables efficient autoregressive generation of RQ codebooks for
    image/audio synthesis with much better quality than flat VQ approaches.
    """

    def __init__(
        self,
        num_tokens: int = 8192,
        dim: int = 512,
        max_spatial_seq_len: int = 256,
        depth_seq_len: int = 8,
        spatial_layers: int = 12,
        depth_layers: int = 4,
        dim_head: int = 64,
        heads: int = 8,
        attn_dropout: float = 0.0,
        ff_mult: int = 4,
        ff_dropout: float = 0.0,
        pad_id: int = 0,
    ):
        super().__init__()
        self.dim = dim
        self.max_spatial_seq_len = max_spatial_seq_len
        self.depth_seq_len = depth_seq_len
        self.pad_id = pad_id

        self.token_emb = nn.Embedding(num_tokens, dim)
        self.spatial_start_token = nn.Parameter(torch.randn(dim))
        self.spatial_pos_emb = nn.Embedding(max_spatial_seq_len + 1, dim)
        self.depth_pos_emb = nn.Embedding(depth_seq_len, dim)

        self.spatial_transformer = RQTransformerStack(
            dim=dim, layers=spatial_layers, dim_head=dim_head,
            heads=heads, ff_mult=ff_mult,
            attn_dropout=attn_dropout, ff_dropout=ff_dropout,
        )

        self.depth_transformer = RQTransformerStack(
            dim=dim, layers=depth_layers, dim_head=dim_head,
            heads=heads, ff_mult=ff_mult,
            attn_dropout=attn_dropout, ff_dropout=ff_dropout,
        )

        self.to_logits = nn.Linear(dim, num_tokens, bias=False)

    @torch.no_grad()
    def generate(
        self,
        prime: Optional[torch.Tensor] = None,
        filter_thres: float = 0.9,
        temperature: float = 1.0,
        default_batch_size: int = 1,
    ) -> torch.Tensor:
        total_seq_len = self.depth_seq_len * self.max_spatial_seq_len
        device = next(self.parameters()).device

        if prime is None:
            prime = torch.empty((default_batch_size, 0), dtype=torch.long, device=device)

        seq = prime
        for _ in range(total_seq_len - seq.shape[-1]):
            logits = self.forward(seq)[:, -1]
            logits = top_k_filtering(logits, thres=filter_thres)
            sampled = gumbel_sample(logits, dim=-1, temperature=temperature)
            seq = torch.cat((seq, rearrange(sampled, 'b -> b 1')), dim=-1)

        return rearrange(seq, 'b (s d) -> b s d', d=self.depth_seq_len)

    def _forward_empty(self, batch_size: int) -> torch.Tensor:
        spatial_tokens = repeat(self.spatial_start_token, 'd -> b 1 d', b=batch_size)
        depth_tokens = self.spatial_transformer(spatial_tokens)
        depth_tokens = self.depth_transformer(depth_tokens)
        return self.to_logits(depth_tokens)

    def forward(self, ids: torch.Tensor, return_loss: bool = False) -> torch.Tensor:
        assert ids.ndim in {2, 3}
        flattened = ids.ndim == 2

        if ids.numel() == 0:
            return self._forward_empty(ids.shape[0])

        if flattened:
            seq_len = ids.shape[-1]
            padding = remainder_to_mult(seq_len, self.depth_seq_len)
            ids = F.pad(ids, (0, padding), value=self.pad_id)
            ids = rearrange(ids, 'b (s d) -> b s d', d=self.depth_seq_len)
        else:
            seq_len = ids.shape[1] * ids.shape[2]

        b, space, depth, device = *ids.shape, ids.device
        assert space <= self.max_spatial_seq_len + 1
        assert depth == self.depth_seq_len

        tokens = self.token_emb(ids)
        spatial_pos = self.spatial_pos_emb(torch.arange(space, device=device))
        depth_pos = self.depth_pos_emb(torch.arange(depth, device=device))

        tokens_with_depth = tokens + depth_pos
        spatial_tokens = reduce(tokens_with_depth, 'b s d f -> b s f', 'sum') + spatial_pos
        spatial_tokens = torch.cat((
            repeat(self.spatial_start_token, 'f -> b 1 f', b=b),
            spatial_tokens,
        ), dim=-2)

        spatial_tokens = self.spatial_transformer(spatial_tokens)
        spatial_tokens = rearrange(spatial_tokens, 'b s f -> b s 1 f')

        tokens_with_depth = F.pad(tokens_with_depth, (0, 0, 0, 0, 0, 1), value=0.0)
        depth_tokens = torch.cat((spatial_tokens, tokens_with_depth), dim=-2)
        depth_tokens = rearrange(depth_tokens, '... n d -> (...) n d')
        depth_tokens = self.depth_transformer(depth_tokens)
        depth_tokens = rearrange(depth_tokens, '(b s) d f -> b s d f', b=b)

        logits = self.to_logits(depth_tokens)
        logits = rearrange(logits, 'b ... f -> b (...) f')
        logits = logits[:, :(seq_len + 1)]

        if not return_loss:
            return logits[:, 1:] if flattened else logits

        logits = logits[:, :-1]
        preds = rearrange(logits, 'b ... c -> b c (...)')
        labels = rearrange(ids, 'b s d -> b (s d)')
        return F.cross_entropy(preds, labels, ignore_index=self.pad_id)
