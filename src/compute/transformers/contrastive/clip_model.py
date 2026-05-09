"""
OMNI Transformer — Contrastive Learning Module
CLIP-style contrastive pretraining for vision-language alignment.
Learned from: openai/CLIP, YilmazKadir/Volt
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ContrastiveLoss(nn.Module):
    """InfoNCE / CLIP-style contrastive loss."""
    def __init__(self, temperature: float = 0.07):
        super().__init__()
        self.temperature = nn.Parameter(torch.tensor(temperature).log())

    def forward(self, image_embeds: torch.Tensor, text_embeds: torch.Tensor) -> Dict[str, torch.Tensor]:
        image_embeds = F.normalize(image_embeds, dim=-1)
        text_embeds = F.normalize(text_embeds, dim=-1)
        temperature = self.temperature.exp().clamp(max=100.0)

        logits = image_embeds @ text_embeds.T * temperature
        labels = torch.arange(logits.size(0), device=logits.device)

        loss_i2t = F.cross_entropy(logits, labels)
        loss_t2i = F.cross_entropy(logits.T, labels)
        loss = (loss_i2t + loss_t2i) / 2

        with torch.inference_mode():
            acc_i2t = (logits.argmax(dim=-1) == labels).float().mean()
            acc_t2i = (logits.T.argmax(dim=-1) == labels).float().mean()

        return {"loss": loss, "loss_i2t": loss_i2t, "loss_t2i": loss_t2i,
                "acc_i2t": acc_i2t.item(), "acc_t2i": acc_t2i.item()}


class CLIPModel(nn.Module):
    """CLIP-style dual encoder for vision-language alignment."""
    def __init__(self, image_encoder: nn.Module, text_encoder: nn.Module,
                 image_dim: int, text_dim: int, embed_dim: int = 512):
        super().__init__()
        self.image_encoder = image_encoder
        self.text_encoder = text_encoder
        self.image_proj = nn.Linear(image_dim, embed_dim)
        self.text_proj = nn.Linear(text_dim, embed_dim)
        self.loss_fn = ContrastiveLoss()

    def encode_image(self, images: torch.Tensor) -> torch.Tensor:
        features = self.image_encoder(images)
        if isinstance(features, dict):
            features = features.get("cls_embedding", features.get("logits")).mean(dim=1) if features.get("cls_embedding") is None else features["cls_embedding"]
        return F.normalize(self.image_proj(features), dim=-1)

    def encode_text(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        features = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask)
        if isinstance(features, dict):
            features = features.get("pooled_output", features.get("last_hidden_state", features.get("logits")).mean(dim=1))
        return F.normalize(self.text_proj(features), dim=-1)

    def forward(self, images: torch.Tensor, input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None) -> Dict:
        image_embeds = self.encode_image(images)
        text_embeds = self.encode_text(input_ids, attention_mask)
        return self.loss_fn(image_embeds, text_embeds)
