import torch
import torch.nn as nn
import torchvision.models as models

class SimCLR(nn.Module):
    def __init__(self, base_model="resnet50", out_dim=128):
        super(SimCLR, self).__init__()
        self.backbone = models.resnet50(pretrained=False)
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        
        # Projection head
        self.projector = nn.Sequential(
            nn.Linear(num_ftrs, num_ftrs),
            nn.ReLU(),
            nn.Linear(num_ftrs, out_dim)
        )

    def forward(self, x):
        h = self.backbone(x)
        z = self.projector(h)
        return h, z
