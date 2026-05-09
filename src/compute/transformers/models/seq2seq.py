"""
OMNI Transformer — Encoder-Decoder (T5/BART style)
Sequence-to-sequence model for translation, summarization.
Learned from: ai-forever/model-zoo, thevasudevgupta/bigbird
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
from ..core import (
    TransformerEncoderBlock, TransformerDecoderBlock,
    AttentionType, NormType, FFNActivation, RMSNorm,
)


@dataclass
class Seq2SeqConfig:
    vocab_size: int = 32128
    embed_dim: int = 768
    encoder_layers: int = 12
    decoder_layers: int = 12
    num_heads: int = 12
    ffn_dim: int = 3072
    max_seq_len: int = 1024
    dropout: float = 0.1
    pad_token_id: int = 0
    eos_token_id: int = 1
    decoder_start_token_id: int = 0


class OmniSeq2Seq(nn.Module):
    """Production encoder-decoder transformer for seq2seq tasks."""
    def __init__(self, config: Seq2SeqConfig):
        super().__init__()
        self.config = config
        self.shared_embed = nn.Embedding(config.vocab_size, config.embed_dim, padding_idx=config.pad_token_id)

        self.encoder_layers = nn.ModuleList([
            TransformerEncoderBlock(
                embed_dim=config.embed_dim, num_heads=config.num_heads,
                ffn_dim=config.ffn_dim, dropout=config.dropout,
                activation=FFNActivation.GELU, norm_type=NormType.LAYER_NORM,
                attention_type=AttentionType.STANDARD, use_rope=False,
            ) for _ in range(config.encoder_layers)
        ])

        self.decoder_layers = nn.ModuleList([
            TransformerDecoderBlock(
                embed_dim=config.embed_dim, num_heads=config.num_heads,
                ffn_dim=config.ffn_dim, dropout=config.dropout,
                activation=FFNActivation.GELU, norm_type=NormType.LAYER_NORM,
                attention_type=AttentionType.STANDARD, use_rope=False,
                has_cross_attention=True,
            ) for _ in range(config.decoder_layers)
        ])

        self.encoder_norm = nn.LayerNorm(config.embed_dim)
        self.decoder_norm = nn.LayerNorm(config.embed_dim)
        self.lm_head = nn.Linear(config.embed_dim, config.vocab_size, bias=False)
        self.lm_head.weight = self.shared_embed.weight  # tie weights

    def encode(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        hidden = self.shared_embed(input_ids)
        mask = None
        if attention_mask is not None:
            mask = (1.0 - attention_mask.unsqueeze(1).unsqueeze(2).float()) * -1e9
        for layer in self.encoder_layers:
            hidden = layer(hidden, attention_mask=mask)
        return self.encoder_norm(hidden)

    def decode(
        self, decoder_input_ids: torch.Tensor, encoder_hidden: torch.Tensor,
        encoder_attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        hidden = self.shared_embed(decoder_input_ids)
        enc_mask = None
        if encoder_attention_mask is not None:
            enc_mask = (1.0 - encoder_attention_mask.unsqueeze(1).unsqueeze(2).float()) * -1e9
        for layer in self.decoder_layers:
            hidden, _ = layer(hidden, encoder_hidden_states=encoder_hidden, encoder_attention_mask=enc_mask)
        return self.decoder_norm(hidden)

    def forward(
        self, input_ids: torch.Tensor, decoder_input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None,
    ) -> dict:
        encoder_hidden = self.encode(input_ids, attention_mask)
        decoder_hidden = self.decode(decoder_input_ids, encoder_hidden, attention_mask)
        logits = self.lm_head(decoder_hidden)
        loss = None
        if labels is not None:
            loss = F.cross_entropy(logits.view(-1, self.config.vocab_size), labels.view(-1), ignore_index=-100)
        return {"logits": logits, "loss": loss, "encoder_hidden": encoder_hidden}
