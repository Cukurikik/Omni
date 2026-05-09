"""
omni_memformer.py — Memory-Augmented Transformer Engine
Inspired by: lucidrains/memformer
Layer: Compute / AI

Implements a Transformer with persistent external memory slots that are
updated via cross-attention and GRU gating at each forward pass.
The memory persists across sequence boundaries enabling long-range reasoning.
"""

import math
import torch
from torch import nn, einsum
import torch.nn.functional as F
from einops import rearrange, repeat
from typing import Optional, Tuple, NamedTuple


class MemformerOutput(NamedTuple):
    encoder_output: torch.Tensor
    memory: torch.Tensor
    decoder_output: Optional[torch.Tensor] = None


class RelativePositionBias(nn.Module):
    """T5-style relative position bias for attention heads."""

    def __init__(self, causal: bool = False, num_buckets: int = 32,
                 max_distance: int = 128, num_heads: int = 8):
        super().__init__()
        self.causal = causal
        self.num_buckets = num_buckets
        self.max_distance = max_distance
        self.relative_attention_bias = nn.Embedding(num_buckets, num_heads)

    @staticmethod
    def _relative_position_bucket(
        relative_position: torch.Tensor, causal: bool = True,
        num_buckets: int = 32, max_distance: int = 128
    ) -> torch.Tensor:
        ret = torch.zeros_like(relative_position, dtype=torch.long)
        n = -relative_position
        if causal:
            num_buckets //= 2
            ret += (n < 0).long() * num_buckets
            n = torch.abs(n)
        else:
            n = torch.max(n, torch.zeros_like(n))

        max_exact = num_buckets // 2
        is_small = n < max_exact
        val_if_large = max_exact + (
            torch.log(n.float() / max_exact)
            / math.log(max_distance / max_exact)
            * (num_buckets - max_exact)
        ).long()
        val_if_large = torch.min(val_if_large, torch.full_like(val_if_large, num_buckets - 1))
        ret += torch.where(is_small, n, val_if_large)
        return ret

    def forward(self, q_len: int, k_len: int) -> torch.Tensor:
        device = self.relative_attention_bias.weight.device
        q_pos = torch.arange(q_len, dtype=torch.long, device=device)
        k_pos = torch.arange(k_len, dtype=torch.long, device=device)
        rel_pos = k_pos[None, :] - q_pos[:, None]
        rp_bucket = self._relative_position_bucket(
            rel_pos, causal=self.causal, num_buckets=self.num_buckets
        )
        values = self.relative_attention_bias(rp_bucket)
        return rearrange(values, 'i j h -> () h i j')


class MemformerAttention(nn.Module):
    """Multi-head attention with optional cross-attention and relative position bias."""

    def __init__(self, dim: int, heads: int = 8, causal: bool = False):
        super().__init__()
        assert dim % heads == 0, "dim must be divisible by heads"
        self.dim_head = dim // heads
        self.scale = self.dim_head ** -0.5
        self.heads = heads
        self.causal = causal

        self.to_q = nn.Linear(dim, dim, bias=False)
        self.to_kv = nn.Linear(dim, dim * 2, bias=False)
        self.to_out = nn.Linear(dim, dim, bias=False)

    def forward(
        self, x: torch.Tensor, context: Optional[torch.Tensor] = None,
        pos_emb: Optional[RelativePositionBias] = None,
        mask: Optional[torch.Tensor] = None,
        attend_self: bool = False,
    ) -> torch.Tensor:
        b, n, _, h = *x.shape, self.heads
        kv_input = x if context is None else context
        if attend_self and context is not None:
            kv_input = torch.cat((x, context), dim=1)

        q = self.to_q(x)
        k, v = self.to_kv(kv_input).chunk(2, dim=-1)
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h=h), (q, k, v))

        dots = einsum('b h i d, b h j d -> b h i j', q, k) * self.scale

        if pos_emb is not None:
            dots = dots + pos_emb(dots.shape[-2], dots.shape[-1])

        if self.causal:
            causal_mask = torch.ones(n, n, device=x.device, dtype=torch.bool).triu(1)
            dots.masked_fill_(causal_mask, -torch.finfo(dots.dtype).max)

        if mask is not None:
            if mask.dim() == 3:
                mask = rearrange(mask, 'b i j -> b () i j')
            dots.masked_fill_(~mask, -torch.finfo(dots.dtype).max)

        attn = dots.softmax(dim=-1)
        out = einsum('b h i j, b h j d -> b h i d', attn, v)
        out = rearrange(out, 'b h n d -> b n (h d)')
        return self.to_out(out)


class MemformerFeedForward(nn.Module):
    def __init__(self, dim: int, mult: int = 4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, dim * mult),
            nn.GELU(),
            nn.Linear(dim * mult, dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class PreNorm(nn.Module):
    def __init__(self, dim: int, fn: nn.Module):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.fn = fn

    def forward(self, x: torch.Tensor, **kwargs) -> torch.Tensor:
        return self.fn(self.norm(x), **kwargs)


class Residual(nn.Module):
    def __init__(self, fn: nn.Module):
        super().__init__()
        self.fn = fn

    def forward(self, x: torch.Tensor, **kwargs) -> torch.Tensor:
        return self.fn(x, **kwargs) + x


class MemformerEncoder(nn.Module):
    def __init__(self, dim: int, depth: int, heads: int = 8):
        super().__init__()
        self.rel_pos = RelativePositionBias(heads=heads)
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(nn.ModuleList([
                Residual(PreNorm(dim, MemformerAttention(dim, heads=heads))),
                Residual(PreNorm(dim, MemformerAttention(dim, heads=heads))),
                Residual(PreNorm(dim, MemformerFeedForward(dim))),
            ]))

    def forward(self, x: torch.Tensor, context: Optional[torch.Tensor] = None) -> torch.Tensor:
        for self_attn, cross_attn, ff in self.layers:
            x = self_attn(x, pos_emb=self.rel_pos)
            if context is not None:
                x = cross_attn(x, context=context)
            x = ff(x)
        return x


class MemformerDecoder(nn.Module):
    def __init__(self, dim: int, depth: int, heads: int = 8):
        super().__init__()
        self.rel_pos = RelativePositionBias(heads=heads, causal=True)
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(nn.ModuleList([
                Residual(PreNorm(dim, MemformerAttention(dim, heads=heads, causal=True))),
                Residual(PreNorm(dim, MemformerAttention(dim, heads=heads))),
                Residual(PreNorm(dim, MemformerFeedForward(dim))),
            ]))

    def forward(self, x: torch.Tensor, context: torch.Tensor) -> torch.Tensor:
        for self_attn, cross_attn, ff in self.layers:
            x = self_attn(x, pos_emb=self.rel_pos)
            x = cross_attn(x, context=context)
            x = ff(x)
        return x


class OmniMemformer(nn.Module):
    """Memory-augmented Transformer with GRU-gated memory updates.

    Memory slots are updated via cross-attention to the encoded sequence,
    then refined through a GRU gate to preserve long-term information.
    """

    def __init__(
        self,
        dim: int = 512,
        num_tokens: int = 30000,
        max_seq_len: int = 1024,
        enc_depth: int = 6,
        dec_depth: int = 6,
        heads: int = 8,
        num_memory_slots: int = 64,
        num_mem_updates: int = 1,
    ):
        super().__init__()
        self.dim = dim
        self.num_mem = num_memory_slots

        self.enc_token_emb = nn.Embedding(num_tokens, dim)
        self.dec_token_emb = nn.Embedding(num_tokens, dim)

        self.encoder = MemformerEncoder(dim, enc_depth, heads)
        self.decoder = MemformerDecoder(dim, dec_depth, heads)

        self.enc_norm = nn.LayerNorm(dim)
        self.dec_norm = nn.LayerNorm(dim)
        self.to_logits = nn.Linear(dim, num_tokens, bias=False)

        self.memory_slots = nn.Parameter(torch.randn(num_memory_slots, dim))
        self.num_mem_updates = num_mem_updates
        self.mem_updater = MemformerAttention(dim, heads=heads)
        self.mem_gru = nn.GRUCell(dim, dim)
        self.mem_ff = Residual(PreNorm(dim, MemformerFeedForward(dim)))

    def get_initial_memory(self, batch_size: int) -> torch.Tensor:
        return repeat(self.memory_slots, 'n d -> b n d', b=batch_size)

    def forward(
        self,
        src: torch.Tensor,
        tgt: Optional[torch.Tensor] = None,
        memory: Optional[torch.Tensor] = None,
    ) -> MemformerOutput:
        b = src.shape[0]
        if memory is None:
            memory = self.get_initial_memory(b)

        enc = self.encoder(self.enc_token_emb(src), context=memory)
        enc = self.enc_norm(enc)

        dec_out = None
        if tgt is not None:
            dec = self.decoder(self.dec_token_emb(tgt), context=enc)
            dec = self.dec_norm(dec)
            dec_out = self.to_logits(dec)

        # Update memory with GRU gating
        for _ in range(self.num_mem_updates):
            prev_mem = memory
            updated = self.mem_updater(memory, context=enc, attend_self=True)
            gated = self.mem_gru(
                rearrange(updated, 'b n d -> (b n) d'),
                rearrange(prev_mem, 'b n d -> (b n) d'),
            )
            memory = rearrange(gated, '(b n) d -> b n d', b=b)
            memory = self.mem_ff(memory)

        return MemformerOutput(
            encoder_output=enc,
            memory=memory,
            decoder_output=dec_out,
        )
