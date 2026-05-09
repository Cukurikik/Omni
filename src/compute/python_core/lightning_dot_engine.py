import torch
import torch.nn as nn
from typing import Dict, Any

class LightningDOTEngine(nn.Module):
    """
    [NAACL 2021] LightningDOT: Pre-trained Vision-and-Language Model for Fast Image-Text Retrieval.
    """
    def __init__(self, visual_dim: int = 2048, textual_dim: int = 768, embed_dim: int = 512):
        super().__init__()
        self.visual_proj = nn.Linear(visual_dim, embed_dim)
        self.textual_proj = nn.Linear(textual_dim, embed_dim)
        self.logit_scale = nn.Parameter(torch.ones([]) * 0.07)

    def forward(self, visual_feats: torch.Tensor, textual_feats: torch.Tensor) -> Dict[str, Any]:
        try:
            v_embed = nn.functional.normalize(self.visual_proj(visual_feats), dim=-1)
            t_embed = nn.functional.normalize(self.textual_proj(textual_feats), dim=-1)
            
            # Cosine similarity
            logit_scale = self.logit_scale.exp()
            logits_per_image = logit_scale * v_embed @ t_embed.t()
            logits_per_text = logits_per_image.t()
            
            return {
                "status": "success",
                "logits_per_image": logits_per_image,
                "logits_per_text": logits_per_text
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
