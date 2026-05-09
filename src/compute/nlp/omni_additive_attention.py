"""
omni_additive_attention.py — Additive (Bahdanau) Attention
Layer: Compute / NLP
Inspired by: d2l-ai/d2l-en

Implements Bahdanau Additive Attention, typically used when Query and Key
vectors have different lengths/dimensions, projecting them into a shared
latent space before applying tanh activation. Zero mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniAdditiveAttention(nn.Module):
    def __init__(self, key_size: int, query_size: int, num_hiddens: int, dropout: float = 0.1):
        super().__init__()
        self.W_k = nn.Linear(key_size, num_hiddens, bias=False)
        self.W_q = nn.Linear(query_size, num_hiddens, bias=False)
        self.w_v = nn.Linear(num_hiddens, 1, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, queries: torch.Tensor, keys: torch.Tensor, values: torch.Tensor, valid_lens: torch.Tensor = None) -> torch.Tensor:
        """
        queries: (Batch, NumQueries, QuerySize)
        keys: (Batch, NumKeys, KeySize)
        values: (Batch, NumKeys, ValueSize)
        valid_lens: (Batch,)
        """
        # queries: (Batch, NumQueries, 1, NumHiddens)
        # keys: (Batch, 1, NumKeys, NumHiddens)
        queries, keys = self.W_q(queries), self.W_k(keys)
        
        # Additive broadcasting: (Batch, NumQueries, NumKeys, NumHiddens)
        features = queries.unsqueeze(2) + keys.unsqueeze(1)
        features = torch.tanh(features)
        
        # Project to single score per Query-Key pair: (Batch, NumQueries, NumKeys, 1)
        scores = self.w_v(features).squeeze(-1) # (Batch, NumQueries, NumKeys)
        
        # Masking out padded tokens
        if valid_lens is not None:
            mask = torch.arange(scores.shape[-1], device=scores.device).expand_as(scores)
            valid_lens_expanded = valid_lens.unsqueeze(1).unsqueeze(2).expand_as(scores)
            scores = torch.where(mask < valid_lens_expanded, scores, torch.full_like(scores, -1e9))

        # Softmax to get attention weights
        attention_weights = F.softmax(scores, dim=-1) # (Batch, NumQueries, NumKeys)
        
        # Apply dropout to attention weights (regularization)
        attention_weights = self.dropout(attention_weights)
        
        # Output: (Batch, NumQueries, ValueSize)
        return torch.bmm(attention_weights, values)
