import torch
import torch.nn as nn
from typing import Dict, List

class OmniPyTorchIE(nn.Module):
    """
    Omni Information Extraction Engine (PyTorch-IE).
    State-of-the-art Information Extraction mapping spans to Named Entities (NER)
    and computing Relation Classification between spans.
    """
    def __init__(self, vocab_size: int, hidden_dim: int = 768, num_entities: int = 9, num_relations: int = 5):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        
        # Core Transformer Encoder for context
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=12, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=6)
        
        # NER Span Classifier
        self.ner_head = nn.Linear(hidden_dim, num_entities)
        
        # Relation Extraction Head (Bilinear projection over pairs)
        self.rel_W = nn.Parameter(torch.Tensor(num_relations, hidden_dim, hidden_dim))
        nn.init.xavier_uniform_(self.rel_W)
        self.rel_bias = nn.Parameter(torch.zeros(num_relations))

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> Dict[str, torch.Tensor]:
        x = self.embedding(input_ids)
        
        # Invert mask for PyTorch transformer
        pad_mask = (attention_mask == 0)
        
        context = self.encoder(x, src_key_padding_mask=pad_mask) # B, L, H
        
        # Predict entities token by token (BIO tagging)
        ner_logits = self.ner_head(context) # B, L, num_entities
        
        # Predict relations between all possible token pairs (L x L)
        # Using bilinear transformation: e1^T W e2
        B, L, H = context.shape
        rel_logits = torch.einsum('bih,rho,bjo->birj', context, self.rel_W, context) + self.rel_bias.view(1, 1, -1, 1)
        
        return {
            "ner_logits": ner_logits,
            "rel_logits": rel_logits
        }
