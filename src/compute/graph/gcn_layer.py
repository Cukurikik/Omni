import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional, Any

class OmniResult:
    def __init__(self, ok: Any = None, err: str = None):
        self.ok = ok
        self.err = err
    
    def is_ok(self) -> bool:
        return self.err is None
        
    def unwrap(self) -> Any:
        if not self.is_ok():
            raise RuntimeError(f"Unwrap failed: {self.err}")
        return self.ok

class GraphConvolution(nn.Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        if bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()

    def reset_parameters(self):
        # Xavier uniform initialization
        stdv = 1. / (self.weight.size(1) ** 0.5)
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        # x: Node features (N, in_features)
        # adj: Adjacency matrix (N, N), ideally sparse and normalized
        support = torch.mm(x, self.weight)
        
        # A * X * W
        if adj.is_sparse:
            output = torch.spmm(adj, support)
        else:
            output = torch.mm(adj, support)
            
        if self.bias is not None:
            return output + self.bias
        else:
            return output

class GCNModel(nn.Module):
    def __init__(self, n_feat: int, n_hidden: int, n_class: int, dropout: float = 0.5):
        super().__init__()
        self.gc1 = GraphConvolution(n_feat, n_hidden)
        self.gc2 = GraphConvolution(n_hidden, n_class)
        self.dropout = dropout

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.gc1(x, adj))
        x = F.dropout(x, self.dropout, training=self.training)
        x = self.gc2(x, adj)
        return F.log_softmax(x, dim=1)

class GCNComputeEngine:
    def __init__(self, device: str = 'cpu'):
        self.device = torch.device(device)

    def compute_forward_pass(self, model: GCNModel, features: torch.Tensor, adj: torch.Tensor) -> OmniResult:
        try:
            model = model.to(self.device)
            features = features.to(self.device)
            adj = adj.to(self.device)
            
            model.eval()
            with torch.no_grad():
                output = model(features, adj)
            
            return OmniResult(ok=output.cpu())
        except Exception as e:
            return OmniResult(err=f"GCN forward pass failed: {str(e)}")
