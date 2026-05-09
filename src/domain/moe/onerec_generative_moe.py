"""
onerec_generative_moe.py — Domain / Recommendation
Layer: Domain / AI — Generative Recommendation MoE

Inspired by OMNI-Multimodal-Intelligent-OneRec-Based-System.
Transforms traditional discriminant recommendation into a generative sequence 
modeling problem using Semantic IDs. Leverages MoE to handle diverse modalities 
(video, text, audio) within the recommendation sequence.
"""

import torch
import torch.nn as nn

class SemanticIDGenerator(nn.Module):
    """
    Generates a unique semantic embedding for a multimodal recommendation item.
    """
    def __init__(self, vocab_size: int, hidden_dim: int):
        super().__init__()
        self.semantic_embedding = nn.Embedding(vocab_size, hidden_dim)
        
    def forward(self, item_ids: torch.Tensor) -> torch.Tensor:
        return self.semantic_embedding(item_ids)

class OneRecGenerativeMoE(nn.Module):
    """
    End-to-end generative recommendation model using Semantic IDs and MoE.
    """
    def __init__(self, vocab_size: int, hidden_dim: int, num_experts: int = 4):
        super().__init__()
        self.semantic_id_gen = SemanticIDGenerator(vocab_size, hidden_dim)
        
        # Simple sequence modeling via Transformer Decoder layer
        self.sequence_model = nn.TransformerEncoderLayer(
            d_model=hidden_dim, 
            nhead=8, 
            dim_feedforward=hidden_dim * 4,
            batch_first=True
        )
        
        # MoE Projection layer tailored for multi-domain (e.g., Short Video, E-commerce, Ads)
        self.moe_gate = nn.Linear(hidden_dim, num_experts)
        self.moe_experts = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_experts)
        ])
        
        # Final projection to next-item Semantic ID probabilities
        self.lm_head = nn.Linear(hidden_dim, vocab_size)

    def forward(self, user_history_ids: torch.Tensor) -> torch.Tensor:
        """
        user_history_ids: (Batch, SeqLen) representing previously interacted items.
        Returns logits over the vocab_size for the next recommended item.
        """
        # Convert IDs to dense Semantic representations
        x = self.semantic_id_gen(user_history_ids)
        
        # Contextualize sequence
        x = self.sequence_model(x)
        
        # Apply Generative MoE to the final token (representing user current state)
        last_state = x[:, -1, :] # (Batch, HiddenDim)
        
        # Routing
        routing_weights = torch.softmax(self.moe_gate(last_state), dim=-1)
        
        moe_out = torch.zeros_like(last_state)
        for e in range(len(self.moe_experts)):
            expert_activation = self.moe_experts[e](last_state)
            weight = routing_weights[:, e].unsqueeze(1)
            moe_out += weight * expert_activation
            
        # Predict next Semantic ID
        next_item_logits = self.lm_head(moe_out)
        return next_item_logits
