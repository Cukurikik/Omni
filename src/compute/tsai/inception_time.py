import torch
import torch.nn as nn

class InceptionModuleTime(nn.Module):
    """
    OMNI Engine: tsai InceptionTime core module for time series classification.
    """
    def __init__(self, in_channels, out_channels, kernel_sizes=[9, 19, 39]):
        super().__init__()
        self.bottleneck = nn.Conv1d(in_channels, out_channels, 1, bias=False) if in_channels > 1 else nn.Identity()
        
        self.convs = nn.ModuleList([
            nn.Conv1d(out_channels if in_channels > 1 else in_channels, out_channels, k, padding=k//2, bias=False)
            for k in kernel_sizes
        ])
        
        self.maxconv = nn.Sequential(
            nn.MaxPool1d(3, stride=1, padding=1),
            nn.Conv1d(in_channels, out_channels, 1, bias=False)
        )
        self.bn = nn.BatchNorm1d(out_channels * 4)
        self.activation = nn.ReLU()

    def forward(self, x):
        x_bot = self.bottleneck(x)
        out = [conv(x_bot) for conv in self.convs]
        out.append(self.maxconv(x))
        out = torch.cat(out, dim=1)
        return self.activation(self.bn(out))
