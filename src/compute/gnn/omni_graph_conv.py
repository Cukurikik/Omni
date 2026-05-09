"""
omni_graph_conv.py — Graph Convolutional Network Layer
Inspired by: RouteFinder / VRP node feature aggregation
Layer: Compute / AI

Implements a Graph Convolutional Network (GCN) layer in PyTorch, used for
aggregating spatial and demand features in Vehicle Routing Problems.
"""

import torch
import torch.nn as nn
import math

class OmniGraphConv(nn.Module):
    """
    Standard Graph Convolutional layer.
    Computes: H' = \sigma( D^{-1/2} A D^{-1/2} H W )
    """
    
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
        stdv = 1.0 / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, NumNodes, InFeatures)
        adj: (Batch, NumNodes, NumNodes) - Normalized Adjacency Matrix
        """
        # Node feature projection: H W
        support = torch.matmul(x, self.weight)
        
        # Neighborhood aggregation: A (H W)
        output = torch.bmm(adj, support)
        
        if self.bias is not None:
            output = output + self.bias
            
        return output

def normalize_adjacency(adj: torch.Tensor) -> torch.Tensor:
    """
    Computes D^{-1/2} A D^{-1/2} given an adjacency matrix A (including self-loops).
    Expects adj to have shape (Batch, N, N)
    """
    # Degree matrix D is the sum of rows
    degree = torch.sum(adj, dim=-1)
    
    # D^{-1/2}
    d_inv_sqrt = torch.pow(degree, -0.5)
    d_inv_sqrt[torch.isinf(d_inv_sqrt)] = 0.0
    
    # Create diagonal matrices for the batch
    d_mat_inv_sqrt = torch.diag_embed(d_inv_sqrt)
    
    # Normalize: D^{-1/2} A D^{-1/2}
    norm_adj = torch.bmm(torch.bmm(d_mat_inv_sqrt, adj), d_mat_inv_sqrt)
    
    return norm_adj
