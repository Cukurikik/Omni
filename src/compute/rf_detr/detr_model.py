import torch
import torch.nn as nn

class RFDETR(nn.Module):
    def __init__(self, num_classes, hidden_dim=256, nheads=8):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )
        self.transformer = nn.Transformer(hidden_dim, nheads)
        self.class_embed = nn.Linear(hidden_dim, num_classes + 1)
        self.bbox_embed = nn.Linear(hidden_dim, 4)
        
    def forward(self, x):
        features = self.backbone(x)
        b, c, h, w = features.shape
        features = features.flatten(2).permute(2, 0, 1)
        hs = self.transformer(features, features)
        outputs_class = self.class_embed(hs)
        outputs_coord = self.bbox_embed(hs).sigmoid()
        return {'pred_logits': outputs_class, 'pred_boxes': outputs_coord}
