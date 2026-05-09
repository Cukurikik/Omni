"""
OMNI Transformer — Causal Language Model (GPT-style)
Full decoder-only model for text generation with KV-cache.
Learned from: Shekswess/tiny-reasoning-language-model, LowinLi/fastgpt
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List
import torch
import torch.nn as nn
import torch.nn.functional as F
from ..core import (
    AttentionConfig, AttentionType, CausalLMBlock, RMSNorm, NormType,
    LearnablePositionalEncoding,
)


@dataclass
class CausalLMConfig:
    vocab_size: int = 32000
    embed_dim: int = 4096
    num_layers: int = 32
    num_heads: int = 32
    num_kv_heads: int = 8
    ffn_dim: int = 14336
    max_seq_len: int = 8192
    dropout: float = 0.0
    norm_eps: float = 1e-6
    tie_word_embeddings: bool = False
    rope_base: float = 10000.0
    attention_type: AttentionType = AttentionType.FLASH


class OmniCausalLM(nn.Module):
    """Production decoder-only transformer for causal language modeling."""

    def __init__(self, config: CausalLMConfig):
        super().__init__()
        self.config = config
        self.embed_tokens = nn.Embedding(config.vocab_size, config.embed_dim)
        self.layers = nn.ModuleList([
            CausalLMBlock(
                embed_dim=config.embed_dim,
                num_heads=config.num_heads,
                num_kv_heads=config.num_kv_heads,
                ffn_dim=config.ffn_dim,
                dropout=config.dropout,
                norm_type=NormType.RMS_NORM,
                attention_type=config.attention_type,
                max_seq_len=config.max_seq_len,
            ) for _ in range(config.num_layers)
        ])
        self.norm = RMSNorm(config.embed_dim, eps=config.norm_eps)
        self.lm_head = nn.Linear(config.embed_dim, config.vocab_size, bias=False)

        if config.tie_word_embeddings:
            self.lm_head.weight = self.embed_tokens.weight

        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        kv_caches: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        use_cache: bool = False,
        labels: Optional[torch.Tensor] = None,
    ) -> dict:
        B, S = input_ids.shape
        hidden = self.embed_tokens(input_ids)
        new_kv_caches = [] if use_cache else None

        for i, layer in enumerate(self.layers):
            cache = kv_caches[i] if kv_caches is not None else None
            hidden, new_cache = layer(
                hidden, attention_mask=attention_mask,
                position_ids=position_ids, kv_cache=cache, use_cache=use_cache,
            )
            if use_cache:
                new_kv_caches.append(new_cache)

        hidden = self.norm(hidden)
        logits = self.lm_head(hidden)

        loss = None
        if labels is not None:
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = labels[:, 1:].contiguous()
            loss = F.cross_entropy(
                shift_logits.view(-1, self.config.vocab_size),
                shift_labels.view(-1),
                ignore_index=-100,
            )

        return {"logits": logits, "loss": loss, "kv_caches": new_kv_caches}

    @torch.inference_mode()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
        eos_token_id: Optional[int] = None,
    ) -> torch.Tensor:
        """Autoregressive generation with top-k/top-p sampling and KV-cache."""
        generated = input_ids
        kv_caches = None

        for _ in range(max_new_tokens):
            inp = generated if kv_caches is None else generated[:, -1:]
            out = self.forward(inp, use_cache=True, kv_caches=kv_caches)
            kv_caches = out["kv_caches"]
            next_logits = out["logits"][:, -1, :] / max(temperature, 1e-6)

            # Top-k filtering
            if top_k > 0:
                v, _ = torch.topk(next_logits, min(top_k, next_logits.size(-1)))
                next_logits[next_logits < v[:, [-1]]] = float("-inf")

            # Top-p (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_idx = torch.sort(next_logits, descending=True)
                cumulative = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                remove = cumulative - F.softmax(sorted_logits, dim=-1) > top_p
                sorted_logits[remove] = float("-inf")
                next_logits = sorted_logits.scatter(1, sorted_idx, sorted_logits)

            probs = F.softmax(next_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            generated = torch.cat([generated, next_token], dim=1)

            if eos_token_id is not None and (next_token == eos_token_id).all():
                break

        return generated
