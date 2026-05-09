import torch
import torch.nn as nn
import torch.optim as optim

class OmniGrokkingModel(nn.Module):
    """OMNI Implementation for studying Grokking on small algorithmic datasets"""
    def __init__(self, vocab_size=100, hidden_dim=128):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, hidden_dim)
        self.mlp = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, vocab_size)
        )

    def forward(self, x1, x2):
        e1 = self.embed(x1)
        e2 = self.embed(x2)
        return self.mlp(torch.cat([e1, e2], dim=-1))

    @staticmethod
    def modular_addition_dataset(p=97):
        """Generates a modular addition dataset: x + y = z (mod p)"""
        x = torch.randint(0, p, (10000,))
        y = torch.randint(0, p, (10000,))
        labels = (x + y) % p
        return x, y, labels
