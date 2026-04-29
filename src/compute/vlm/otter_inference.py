import torch
import torch.nn as nn

class OtterVLM(nn.Module):
    def __init__(self):
        super().__init__()
        self.vision_encoder = nn.Linear(512, 256)
        self.text_decoder = nn.Linear(256, 1024)

    def forward(self, image_features: torch.Tensor) -> torch.Tensor:
        try:
            hidden = self.vision_encoder(image_features)
            logits = self.text_decoder(hidden)
            return logits
        except Exception as e:
            raise RuntimeError(f"Otter VLM inference failed: {e}")
