import torch
import torch.nn as nn
from typing import Tuple

class OmniTPSRPlanner(nn.Module):
    """
    Omni Transformer-based Planning for Symbolic Regression (TPSR).
    Leverages planning algorithms embedded within transformer topologies to
    discover interpretable mathematical equations from numerical data streams.
    """
    def __init__(self, input_dim: int = 1, hidden_dim: int = 256, max_equation_len: int = 64, vocab_size: int = 30):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.max_equation_len = max_equation_len
        self.vocab_size = vocab_size
        
        # Project numerical data (e.g. x, y pairs) to hidden dimension
        self.data_encoder = nn.Sequential(
            nn.Linear(input_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Equation tokens embeddings
        self.token_embedding = nn.Embedding(vocab_size, hidden_dim)
        self.pos_embedding = nn.Parameter(torch.zeros(1, max_equation_len, hidden_dim))
        
        # Planner Transformer (Decodes the skeleton of the equation)
        decoder_layer = nn.TransformerDecoderLayer(d_model=hidden_dim, nhead=8, batch_first=True)
        self.planner = nn.TransformerDecoder(decoder_layer, num_layers=6)
        
        # Monte-Carlo Tree Search (MCTS) Value Head
        self.value_head = nn.Linear(hidden_dim, 1)
        # Policy Head
        self.policy_head = nn.Linear(hidden_dim, vocab_size)

    def forward(self, dataset: torch.Tensor, partial_eq: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        dataset: [Batch, N_samples, 2] (x, y)
        partial_eq: [Batch, seq_len] tokens
        """
        B, N, _ = dataset.shape
        _, seq_len = partial_eq.shape
        
        # Encode dataset points and aggregate
        data_feats = self.data_encoder(dataset) # B, N, H
        memory = data_feats.mean(dim=1).unsqueeze(1) # B, 1, H
        
        # Encode partial equation
        eq_emb = self.token_embedding(partial_eq) + self.pos_embedding[:, :seq_len, :]
        
        # Causal mask
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(seq_len, device=dataset.device)
        
        # Plan the next token
        out = self.planner(eq_emb, memory, tgt_mask=tgt_mask)
        
        # Predict Policy (next token) and Value (expected reward/fitness)
        logits = self.policy_head(out)
        value = self.value_head(out[:, -1, :])
        
        return logits, value
