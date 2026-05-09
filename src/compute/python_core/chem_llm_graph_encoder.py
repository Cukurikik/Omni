import torch
import torch.nn as nn
from typing import Dict, Any

class ChemGraphEncoder(nn.Module):
    def __init__(self, node_dim: int):
        super().__init__()
        self.linear = nn.Linear(node_dim, node_dim)

    def forward(self, node_features: torch.Tensor, adj_matrix: torch.Tensor) -> Dict[str, Any]:
        try:
            out = self.linear(torch.matmul(adj_matrix, node_features))
            return {"status": "success", "graph_embedding": out}
        except Exception as e:
            return {"status": "error", "message": str(e)}
