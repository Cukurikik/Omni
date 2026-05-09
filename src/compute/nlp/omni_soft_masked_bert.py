"""
omni_soft_masked_bert.py — Soft-Masked BERT Architecture
Layer: Compute / AI
Inspired by: gitabtion/SoftMaskedBert-PyTorch

Implements the Soft-Masked BERT model for Chinese/English spelling error correction.
Consists of a Bi-GRU detection network feeding "soft-masked" embeddings into
a BERT correction network. Zero-mock.
"""

import torch
import torch.nn as nn

class OmniSoftMaskedBert(nn.Module):
    def __init__(self, vocab_size: int, hidden_dim: int, num_layers: int = 12, num_heads: int = 12):
        super().__init__()
        self.hidden_dim = hidden_dim
        
        # 1. Shared Embedding Layer
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        
        # Standard BERT mask token embedding (Learnable)
        self.mask_embedding = nn.Parameter(torch.randn(hidden_dim))

        # 2. Detection Network: Bi-GRU
        self.detector = nn.GRU(
            input_size=hidden_dim,
            hidden_size=hidden_dim // 2,
            num_layers=1,
            batch_first=True,
            bidirectional=True
        )
        self.detector_linear = nn.Linear(hidden_dim, 1) # Outputs probability of error

        # 3. Correction Network: Standard Transformer Encoder (BERT)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4,
            batch_first=True,
            activation="gelu"
        )
        self.corrector = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # 4. Final Output Projection
        self.output_layer = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x: torch.Tensor):
        """
        x: (Batch, SeqLen) of token IDs
        Returns:
            p_error: (Batch, SeqLen) Error probabilities from detector
            logits: (Batch, SeqLen, VocabSize) Correction logits
        """
        # (Batch, SeqLen, HiddenDim)
        embeds = self.embedding(x) 

        # --- Detection Phase ---
        # detector_out: (Batch, SeqLen, HiddenDim)
        detector_out, _ = self.detector(embeds)
        
        # Probability of each token being an error
        # (Batch, SeqLen, 1)
        p_error = torch.sigmoid(self.detector_linear(detector_out)) 

        # --- Soft Masking Phase ---
        # If p_error is high, we rely more on the mask_embedding.
        # If p_error is low, we rely more on the original embeds.
        # soft_embeds = (1 - p) * embeds + p * mask_embed
        
        mask_embeds_expanded = self.mask_embedding.view(1, 1, -1).expand_as(embeds)
        soft_embeds = (1.0 - p_error) * embeds + p_error * mask_embeds_expanded

        # --- Correction Phase ---
        # The corrector sees the soft-masked embeddings
        # (Batch, SeqLen, HiddenDim)
        corrector_out = self.corrector(soft_embeds)
        
        # Project back to vocabulary
        # (Batch, SeqLen, VocabSize)
        logits = self.output_layer(corrector_out)
        
        # Residual connection from embeddings (optional, typical in spell correction)
        # logits = logits + self.output_layer(embeds)

        return p_error.squeeze(-1), logits
