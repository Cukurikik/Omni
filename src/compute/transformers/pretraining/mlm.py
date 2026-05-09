"""
OMNI Transformer — Masked Language Model for Pretraining
MLM pretraining head (BERT-style).
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict
import random


class MLMHead(nn.Module):
    """Masked Language Modeling head for BERT pretraining."""
    def __init__(self, embed_dim: int, vocab_size: int):
        super().__init__()
        self.dense = nn.Linear(embed_dim, embed_dim)
        self.activation = nn.GELU()
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.decoder = nn.Linear(embed_dim, vocab_size)

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.layer_norm(self.activation(self.dense(hidden))))


class MLMDataProcessor:
    """Process data for masked language modeling."""
    def __init__(self, vocab_size: int, mask_token_id: int = 4, mask_prob: float = 0.15):
        self.vocab_size = vocab_size
        self.mask_token_id = mask_token_id
        self.mask_prob = mask_prob

    def mask_tokens(self, input_ids: torch.Tensor) -> tuple:
        labels = input_ids.clone()
        probability_matrix = torch.full(labels.shape, self.mask_prob)
        masked_indices = torch.bernoulli(probability_matrix).bool()
        labels[~masked_indices] = -100  # Only compute loss on masked

        # 80% -> [MASK], 10% -> random, 10% -> original
        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        input_ids[indices_replaced] = self.mask_token_id
        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(self.vocab_size, labels.shape)
        input_ids[indices_random] = random_words[indices_random]
        return input_ids, labels
