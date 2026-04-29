import torch
import torch.nn as nn

class OmniGNNLayer(nn.Module):
    def __init__(self, in_feat: int, out_feat: int):
        super().__init__()
        self.linear = nn.Linear(in_feat, out_feat)
        
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        # D^-1/2 A D^-1/2 X W
        h = self.linear(x)
        return torch.matmul(adj, h)
