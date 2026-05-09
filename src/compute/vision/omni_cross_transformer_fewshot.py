# OMNI Compute & AI Layer
# Cross Transformers for Spatially-Aware Few-Shot Transfer
# Inspired by lucidrains/cross-transformers-pytorch.

import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange

class OmniCrossTransformerFewShot(nn.Module):
    """
    Cross Transformer implementation tailored for the Omni Universal Engine.
    Aligns spatial features between query images and few-shot support set images.
    """
    def __init__(self, dim: int, heads: int = 8, dim_head: int = 64):
        super().__init__()
        self.scale = dim_head ** -0.5
        self.heads = heads
        inner_dim = dim_head * heads

        self.to_q = nn.Linear(dim, inner_dim, bias=False)
        self.to_kv = nn.Linear(dim, inner_dim * 2, bias=False)
        self.to_out = nn.Linear(inner_dim, dim)

    def forward(self, query_features: torch.Tensor, support_features: torch.Tensor) -> torch.Tensor:
        """
        query_features: [batch, query_spatial_pts, dim]
        support_features: [batch, support_spatial_pts, dim]
        """
        h = self.heads
        
        q = self.to_q(query_features)
        k, v = self.to_kv(support_features).chunk(2, dim=-1)

        # Rearrange for multi-head attention
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h=h), (q, k, v))

        # Cross attention: Queries (from Query image) attend to Keys/Values (from Support image)
        sim = torch.einsum('b h i d, b h j d -> b h i j', q, k) * self.scale
        
        attn = sim.softmax(dim=-1)
        
        out = torch.einsum('b h i j, b h j d -> b h i d', attn, v)
        out = rearrange(out, 'b h n d -> b n (h d)')
        
        return self.to_out(out)

class OmniFewShotClassifier(nn.Module):
    def __init__(self, feature_extractor: nn.Module, cross_transformer: OmniCrossTransformerFewShot):
        super().__init__()
        self.feature_extractor = feature_extractor
        self.cross_transformer = cross_transformer

    def forward(self, query_img: torch.Tensor, support_imgs: torch.Tensor, support_labels: torch.Tensor):
        # Extract spatial features (e.g., from a ResNet or ViT backbone before pooling)
        q_feat = self.feature_extractor(query_img)
        s_feat = self.feature_extractor(support_imgs)
        
        # Align query spatial features to support spatial features
        aligned_features = self.cross_transformer(q_feat, s_feat)
        
        # Omni Engine: Proceed to distance metric (e.g., Mahalanobis or Euclidean) 
        # to classify the query against the aligned support set.
        return aligned_features
