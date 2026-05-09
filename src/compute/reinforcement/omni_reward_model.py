"""
omni_reward_model.py — RLHF Reward Model
Layer: Compute / AI

Implements a Bradley-Terry reward model used in Reinforcement Learning 
from Human Feedback (RLHF) to score completions for PPO algorithms.
"""

import torch
import torch.nn as nn
from typing import Dict

class OmniRewardModel(nn.Module):
    """
    A Transformer encoder topped with a scalar regression head.
    Predicts a single scalar reward representing human preference.
    """
    
    def __init__(self, vocab_size: int = 50257, hidden_size: int = 768):
        super().__init__()
        
        # Standard Token Embeddings
        self.embed = nn.Embedding(vocab_size, hidden_size)
        
        # Transformer backbone (Mock configuration for RLHF setup)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size, 
            nhead=12, 
            dim_feedforward=3072, 
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=4)
        
        # Regression head outputting a single reward scalar
        self.value_head = nn.Linear(hidden_size, 1, bias=False)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        input_ids: (Batch, SeqLen)
        Returns: (Batch,) representing the reward score for the sequence.
        """
        x = self.embed(input_ids)
        
        padding_mask = ~attention_mask.bool()
        hidden = self.encoder(x, src_key_padding_mask=padding_mask)
        
        # Pool the representation of the last non-padded token
        # For simplicity in this mock, we just take the first token (CLS equivalent)
        # or the mean. Let's use mean pooling.
        
        active_hidden = hidden * attention_mask.unsqueeze(-1)
        sum_hidden = active_hidden.sum(dim=1)
        lengths = attention_mask.sum(dim=1, keepdim=True).clamp(min=1e-9)
        pooled = sum_hidden / lengths
        
        # Get scalar reward
        reward = self.value_head(pooled).squeeze(-1)
        return reward

    def compute_loss(self, 
                     chosen_ids: torch.Tensor, chosen_mask: torch.Tensor,
                     rejected_ids: torch.Tensor, rejected_mask: torch.Tensor) -> torch.Tensor:
        """
        Computes the Bradley-Terry ranking loss.
        The model should predict a higher reward for the chosen completion.
        """
        reward_chosen = self(chosen_ids, chosen_mask)
        reward_rejected = self(rejected_ids, rejected_mask)
        
        # Loss = -log(sigmoid(reward_chosen - reward_rejected))
        diff = reward_chosen - reward_rejected
        loss = -torch.nn.functional.logsigmoid(diff).mean()
        
        return loss
