import torch
import torch.nn as nn

# OMNI MOTHER: muMoE - Multilinear Mixture of Experts
# Scalable Expert Specialization through Factorization (NeurIPS'24)

class OmniMuMoEFactorizedExpert(nn.Module):
    def __init__(self, hidden_dim: int, rank: int):
        super().__init__()
        # Decompose W into A * B for extreme parameter efficiency
        self.A = nn.Linear(hidden_dim, rank, bias=False)
        self.B = nn.Linear(rank, hidden_dim, bias=True)
        self.activation = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.A(x)
        x = self.activation(x)
        x = self.B(x)
        return x
