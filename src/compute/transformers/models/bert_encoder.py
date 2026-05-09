"""
OMNI Transformer — BERT Encoder for NLU Tasks
Text classification, NER, sequence labeling.
Learned from: retarfi/language-pretraining, dipanjanS/adv_nlp_workshop,
              Kaleidophon/token2index
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from ..core import TransformerEncoderBlock, AttentionType, NormType, FFNActivation


@dataclass
class BERTConfig:
    vocab_size: int = 30522
    embed_dim: int = 768
    num_layers: int = 12
    num_heads: int = 12
    ffn_dim: int = 3072
    max_seq_len: int = 512
    num_labels: int = 2
    dropout: float = 0.1
    pad_token_id: int = 0
    type_vocab_size: int = 2
    task: str = "classification"  # "classification", "ner", "embedding"


class BERTEmbeddings(nn.Module):
    def __init__(self, config: BERTConfig):
        super().__init__()
        self.word_embeddings = nn.Embedding(config.vocab_size, config.embed_dim, padding_idx=config.pad_token_id)
        self.position_embeddings = nn.Embedding(config.max_seq_len, config.embed_dim)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.embed_dim)
        self.layer_norm = nn.LayerNorm(config.embed_dim, eps=1e-12)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, input_ids: torch.Tensor, token_type_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, S = input_ids.shape
        position_ids = torch.arange(S, device=input_ids.device).unsqueeze(0)
        if token_type_ids is None:
            token_type_ids = torch.zeros_like(input_ids)
        embeddings = self.word_embeddings(input_ids) + self.position_embeddings(position_ids) + self.token_type_embeddings(token_type_ids)
        return self.dropout(self.layer_norm(embeddings))


class OmniBERT(nn.Module):
    """Production BERT encoder for classification, NER, and embedding tasks."""
    def __init__(self, config: BERTConfig):
        super().__init__()
        self.config = config
        self.embeddings = BERTEmbeddings(config)
        self.encoder = nn.ModuleList([
            TransformerEncoderBlock(
                embed_dim=config.embed_dim, num_heads=config.num_heads,
                ffn_dim=config.ffn_dim, dropout=config.dropout,
                activation=FFNActivation.GELU, norm_type=NormType.LAYER_NORM,
                attention_type=AttentionType.STANDARD, use_rope=False,
            ) for _ in range(config.num_layers)
        ])
        self.pooler = nn.Sequential(nn.Linear(config.embed_dim, config.embed_dim), nn.Tanh())

        if config.task == "classification":
            self.classifier = nn.Linear(config.embed_dim, config.num_labels)
        elif config.task == "ner":
            self.classifier = nn.Linear(config.embed_dim, config.num_labels)
        else:
            self.classifier = None

    def forward(
        self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None,
    ) -> dict:
        hidden = self.embeddings(input_ids, token_type_ids)

        if attention_mask is not None:
            ext_mask = (1.0 - attention_mask.unsqueeze(1).unsqueeze(2).float()) * -1e9
        else:
            ext_mask = None

        for layer in self.encoder:
            hidden = layer(hidden, attention_mask=ext_mask)

        pooled = self.pooler(hidden[:, 0])
        result = {"last_hidden_state": hidden, "pooled_output": pooled}

        if self.classifier is not None and labels is not None:
            if self.config.task == "classification":
                logits = self.classifier(pooled)
                result["logits"] = logits
                result["loss"] = F.cross_entropy(logits, labels)
            elif self.config.task == "ner":
                logits = self.classifier(hidden)
                result["logits"] = logits
                result["loss"] = F.cross_entropy(logits.view(-1, self.config.num_labels), labels.view(-1), ignore_index=-100)
        elif self.classifier is not None:
            result["logits"] = self.classifier(pooled if self.config.task == "classification" else hidden)

        return result
