import torch
import torch.nn as nn
import torch.nn.functional as F

class BackgroundMattingNet(nn.Module):
    def __init__(self):
        super().__init__()
        # Simplified MobileNetV2 style backbone
        self.conv1 = nn.Conv2d(6, 32, kernel_size=3, stride=2, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1)
        self.alpha_out = nn.Conv2d(64, 1, kernel_size=1)

    def forward(self, img, bg):
        x = torch.cat([img, bg], dim=1)
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.interpolate(x, scale_factor=4, mode='bilinear', align_corners=False)
        alpha = torch.sigmoid(self.alpha_out(x))
        return alpha

if __name__ == "__main__":
    net = BackgroundMattingNet()
    img = torch.randn(1, 3, 256, 256)
    bg = torch.randn(1, 3, 256, 256)
    alpha = net(img, bg)
    print(f"Alpha matte shape: {alpha.shape}")
