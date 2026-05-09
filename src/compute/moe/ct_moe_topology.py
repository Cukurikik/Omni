"""
ct_moe_topology.py — Compute / Architecture
Layer: Compute / AI — Collaborative Topology MoE

Inspired by CT-MoE (Learning Expert Collaboration Topology).
Unlike standard MoE where experts are completely independent, CT-MoE learns a 
collaboration graph/topology, allowing adjacent experts in the graph to 
share activations or fuse outputs for better semantic continuity.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class CTMoE(nn.Module):
    """
    Mixture of Experts with learned Collaboration Topology.
    """
    def __init__(self, hidden_dim: int, num_experts: int = 8, top_k: int = 2):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_experts = num_experts
        self.top_k = top_k
        
        # Standard Gating Network
        self.gate = nn.Linear(hidden_dim, num_experts, bias=False)
        
        # The Learned Topology Matrix (Adjacency Matrix between experts)
        # Initialized as an identity matrix (no collaboration), but learns over time
        self.topology_matrix = nn.Parameter(torch.eye(num_experts))
        
        # Dummy experts for zero-mock execution
        self.experts = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, SeqLen, HiddenDim)
        """
        batch_size, seq_len, hidden_dim = x.shape
        flat_x = x.view(-1, hidden_dim)
        
        # 1. Routing Probabilities
        logits = self.gate(flat_x)
        routing_weights = F.softmax(logits, dim=-1)
        
        # 2. Apply Learned Topology
        # By multiplying the routing weights by the topology matrix, we spread
        # the activation probability to "collaborator" experts.
        # Ensure topology remains positive
        positive_topology = F.relu(self.topology_matrix)
        collaborative_weights = torch.matmul(routing_weights, positive_topology)
        
        # 3. Top-K Selection based on collaborative weights
        top_k_weights, top_k_indices = torch.topk(collaborative_weights, self.top_k, dim=-1)
        top_k_weights = top_k_weights / top_k_weights.sum(dim=-1, keepdim=True)
        
        # 4. Expert Execution
        final_output = torch.zeros_like(flat_x)
        
        for i in range(flat_x.shape[0]):
            token_x = flat_x[i].unsqueeze(0)
            token_out = torch.zeros_like(token_x)
            
            for k in range(self.top_k):
                expert_idx = top_k_indices[i, k].item()
                weight = top_k_weights[i, k].item()
                
                expert_output = self.experts[expert_idx](token_x)
                token_out += weight * expert_output
                
            final_output[i] = token_out.squeeze(0)
            
        return final_output.view(batch_size, seq_len, hidden_dim)
