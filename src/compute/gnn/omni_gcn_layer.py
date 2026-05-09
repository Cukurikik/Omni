"""
omni_gcn_layer.py — Graph Convolutional Network (GCN) Layer
Layer: Compute / GNN
Inspired by: rusty1s/pytorch_geometric

Implements a standard GCN layer passing messages along edges of a graph.
Utilizes sparse matrix operations to handle highly unstructured, large-scale 
graph datasets (like social networks or molecular structures). Zero mock.
"""

import torch
import torch.nn as nn
import math

class OmniGraphConv(nn.Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        self.weight = nn.Parameter(torch.Tensor(in_features, out_features))
        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias', None)
            
        self.reset_parameters()

    def reset_parameters(self):
        stdv = 1.0 / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)

    def forward(self, node_features: torch.Tensor, adjacency_matrix: torch.Tensor) -> torch.Tensor:
        """
        node_features: (NumNodes, InFeatures)
        adjacency_matrix: (NumNodes, NumNodes) - Usually a SparseTensor
        
        Formula: H^{(l+1)} = \sigma( \hat{D}^{-1/2} \hat{A} \hat{D}^{-1/2} H^{(l)} W^{(l)} )
        For simplicity, we assume adjacency_matrix is already symmetrically normalized with self-loops added.
        """
        # Step 1: Linear Transformation (H * W)
        # support: (NumNodes, OutFeatures)
        support = torch.matmul(node_features, self.weight)
        
        # Step 2: Message Passing via Adjacency Matrix (A * (HW))
        # If adjacency_matrix is sparse, torch.sparse.mm handles it efficiently
        if adjacency_matrix.is_sparse:
            output = torch.sparse.mm(adjacency_matrix, support)
        else:
            output = torch.matmul(adjacency_matrix, support)
            
        # Step 3: Add bias
        if self.bias is not None:
            output = output + self.bias
            
        return output

class OmniGCN(nn.Module):
    def __init__(self, num_node_features: int, hidden_dim: int, num_classes: int):
        super().__init__()
        self.conv1 = OmniGraphConv(num_node_features, hidden_dim)
        self.conv2 = OmniGraphConv(hidden_dim, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x, adj)
        x = self.relu(x)
        x = self.conv2(x, adj)
        return x
