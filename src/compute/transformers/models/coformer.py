"""
OMNI Transformer — Collaborative Transformer (CoFormer)
Grounded Situation Recognition with collaborative glance-gaze attention.
Learned from: jhcho99/CoFormer (CVPR 2022)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class CoFormerConfig:
    embed_dim: int = 256
    num_layers: int = 3
    num_heads: int = 8
    ffn_dim: int = 2048
    num_roles: int = 190
    num_verbs: int = 504
    num_nouns: int = 11000
    dropout: float = 0.1


class GlanceTransformer(nn.Module):
    """Glance transformer: identifies overall activity and roles."""
    def __init__(self, config: CoFormerConfig):
        super().__init__()
        self.verb_embed = nn.Embedding(config.num_verbs, config.embed_dim)
        self.role_queries = nn.Embedding(config.num_roles, config.embed_dim)
        self.layers = nn.ModuleList()
        for _ in range(config.num_layers):
            self.layers.append(nn.TransformerDecoderLayer(
                d_model=config.embed_dim, nhead=config.num_heads,
                dim_feedforward=config.ffn_dim, dropout=config.dropout, batch_first=True,
            ))
        self.verb_classifier = nn.Linear(config.embed_dim, config.num_verbs)

    def forward(self, image_features: torch.Tensor, role_ids: Optional[torch.Tensor] = None) -> Dict:
        B = image_features.shape[0]
        # Use role queries as decoder input
        if role_ids is not None:
            queries = self.role_queries(role_ids)
        else:
            queries = self.role_queries.weight.unsqueeze(0).expand(B, -1, -1)

        for layer in self.layers:
            queries = layer(queries, image_features)

        # Global verb prediction from pooled features
        pooled = image_features.mean(dim=1)
        verb_logits = self.verb_classifier(pooled)
        return {"role_features": queries, "verb_logits": verb_logits}


class GazeTransformer(nn.Module):
    """Gaze transformer: refines role understanding with focused attention."""
    def __init__(self, config: CoFormerConfig):
        super().__init__()
        self.layers = nn.ModuleList()
        for _ in range(config.num_layers):
            self.layers.append(nn.TransformerDecoderLayer(
                d_model=config.embed_dim, nhead=config.num_heads,
                dim_feedforward=config.ffn_dim, dropout=config.dropout, batch_first=True,
            ))
        self.noun_classifier = nn.Linear(config.embed_dim, config.num_nouns)

    def forward(self, role_features: torch.Tensor, image_features: torch.Tensor) -> Dict:
        x = role_features
        for layer in self.layers:
            x = layer(x, image_features)
        noun_logits = self.noun_classifier(x)
        return {"refined_features": x, "noun_logits": noun_logits}


class OmniCoFormer(nn.Module):
    """Full collaborative transformer for grounded situation recognition."""
    def __init__(self, config: CoFormerConfig):
        super().__init__()
        self.glance = GlanceTransformer(config)
        self.gaze = GazeTransformer(config)

    def forward(self, image_features: torch.Tensor, role_ids: Optional[torch.Tensor] = None,
                verb_labels: Optional[torch.Tensor] = None, noun_labels: Optional[torch.Tensor] = None) -> Dict:
        glance_out = self.glance(image_features, role_ids)
        gaze_out = self.gaze(glance_out["role_features"], image_features)

        loss = None
        if verb_labels is not None and noun_labels is not None:
            verb_loss = F.cross_entropy(glance_out["verb_logits"], verb_labels)
            noun_loss = F.cross_entropy(gaze_out["noun_logits"].view(-1, gaze_out["noun_logits"].size(-1)),
                                        noun_labels.view(-1), ignore_index=-100)
            loss = verb_loss + noun_loss

        return {"verb_logits": glance_out["verb_logits"], "noun_logits": gaze_out["noun_logits"],
                "loss": loss, "role_features": gaze_out["refined_features"]}
