"""
omni_coco_lm_model.py — COCO-LM Model Architecture
Inspired by: COCO-LM
Layer: Compute / AI

Defines the Generator and Discriminator architecture for Correcting and 
Contrasting Text Sequences.
"""

import torch
import torch.nn as nn
from typing import Dict, Tuple

class OmniCOCOLM(nn.Module):
    """
    COCO-LM Architecture featuring a small Generator (for MLM)
    and a larger Discriminator (for Sequence Correcting and Contrasting).
    """

    def __init__(self, 
                 vocab_size: int = 30522, 
                 gen_hidden: int = 256, 
                 disc_hidden: int = 768,
                 gen_layers: int = 4,
                 disc_layers: int = 12):
        super().__init__()
        self.vocab_size = vocab_size
        
        # Shared token embeddings
        self.embeddings = nn.Embedding(vocab_size, disc_hidden)
        self.gen_embedding_proj = nn.Linear(disc_hidden, gen_hidden)
        
        # Generator (Predicts MLM tokens)
        gen_layer = nn.TransformerEncoderLayer(d_model=gen_hidden, nhead=4, dim_feedforward=1024, batch_first=True)
        self.generator = nn.TransformerEncoder(gen_layer, num_layers=gen_layers)
        self.gen_head = nn.Linear(gen_hidden, vocab_size)
        
        # Discriminator (Corrects sequences and aligns representations)
        disc_layer = nn.TransformerEncoderLayer(d_model=disc_hidden, nhead=12, dim_feedforward=3072, batch_first=True)
        self.discriminator = nn.TransformerEncoder(disc_layer, num_layers=disc_layers)
        
    def forward_generator(self, input_ids: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Forward pass for the generator."""
        x = self.embeddings(input_ids)
        x = self.gen_embedding_proj(x)
        
        padding_mask = ~mask.bool()
        encoded = self.generator(x, src_key_padding_mask=padding_mask)
        
        logits = self.gen_head(encoded)
        return logits

    def forward_discriminator(self, input_ids: torch.Tensor, mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for the discriminator.
        Returns full hidden states and the CLS representation.
        """
        x = self.embeddings(input_ids)
        
        padding_mask = ~mask.bool()
        hidden_states = self.discriminator(x, src_key_padding_mask=padding_mask)
        
        # CLS token is at index 0
        cls_rep = hidden_states[:, 0, :]
        return hidden_states, cls_rep

    def generate_corrupted_sequence(self, input_ids: torch.Tensor, mlm_mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Replaces masked tokens with generator predictions.
        mlm_mask: 1 if masked, 0 otherwise
        """
        with torch.no_grad():
            gen_logits = self.forward_generator(input_ids, torch.ones_like(input_ids))
            # Sample from generator
            probs = torch.softmax(gen_logits, dim=-1)
            sampled_tokens = torch.multinomial(probs.view(-1, self.vocab_size), 1).view(*input_ids.shape)
            
        corrupted_ids = input_ids.clone()
        corrupted_ids[mlm_mask.bool()] = sampled_tokens[mlm_mask.bool()]
        
        # Return corrupted sequence and mask indicating which tokens were changed
        changed_mask = (corrupted_ids != input_ids) & mlm_mask.bool()
        return corrupted_ids, changed_mask
