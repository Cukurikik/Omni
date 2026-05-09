"""
moe_hierarchical_clustering.py — Compute / ClusterMoE
Layer: Compute / AI — Hierarchical Expert Routing

Implements ClusterMoE dynamic tree-based routing. Instead of a flat routing
projection which struggles to scale to thousands of experts, this uses a 
hierarchical tree router. Tokens are first routed to expert clusters, and then
to specific experts within the cluster, dramatically reducing routing complexity
and improving semantic specialization.
"""
import torch
import torch.nn as nn
from typing import Tuple

class HierarchicalClusterRouter(nn.Module):
    """
    Tree-based router that routes tokens through a hierarchy of clusters.
    Complexity drops from O(N_experts) to O(N_clusters + Experts_per_cluster).
    """
    def __init__(self, dim: int, num_clusters: int, experts_per_cluster: int, top_k_clusters: int = 1, top_k_experts: int = 2):
        super().__init__()
        self.dim = dim
        self.num_clusters = num_clusters
        self.experts_per_cluster = experts_per_cluster
        self.top_k_clusters = top_k_clusters
        self.top_k_experts = top_k_experts
        
        # Level 1: Cluster Routing
        self.cluster_gate = nn.Linear(dim, num_clusters, bias=False)
        
        # Level 2: Expert Routing within Clusters
        # Parameterized as a 3D tensor to hold gates for each cluster independently
        self.expert_gates = nn.Parameter(torch.randn(num_clusters, dim, experts_per_cluster))
        nn.init.normal_(self.expert_gates, std=0.02)

    def forward(self, hidden_states: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            hidden_states: (batch_size * seq_len, dim)
        Returns:
            final_routing_weights: (N, top_k_clusters * top_k_experts)
            final_expert_indices: (N, top_k_clusters * top_k_experts) mapped to global IDs
        """
        N, D = hidden_states.shape
        
        # 1. Route to Clusters
        cluster_logits = self.cluster_gate(hidden_states) # (N, num_clusters)
        cluster_probs = torch.softmax(cluster_logits, dim=-1)
        top_cluster_weights, top_cluster_indices = torch.topk(cluster_probs, self.top_k_clusters, dim=-1)
        
        final_weights = []
        final_indices = []
        
        # 2. Route to Experts within selected clusters
        for k in range(self.top_k_clusters):
            c_indices = top_cluster_indices[:, k] # (N,)
            c_weights = top_cluster_weights[:, k] # (N,)
            
            # Select the expert gate weights for the chosen clusters
            # hidden_states: (N, 1, D)
            # selected_gates: (N, D, experts_per_cluster)
            selected_gates = self.expert_gates[c_indices] 
            
            # Compute expert logits: (N, 1, D) @ (N, D, E) -> (N, 1, E) -> (N, E)
            expert_logits = torch.bmm(hidden_states.unsqueeze(1), selected_gates).squeeze(1)
            expert_probs = torch.softmax(expert_logits, dim=-1)
            
            top_exp_weights, top_exp_indices = torch.topk(expert_probs, self.top_k_experts, dim=-1)
            
            # Combine weights: P(Cluster) * P(Expert | Cluster)
            combined_weights = c_weights.unsqueeze(-1) * top_exp_weights
            
            # Map local expert index to global expert index
            # Global ID = cluster_id * experts_per_cluster + local_expert_id
            global_exp_indices = (c_indices.unsqueeze(-1) * self.experts_per_cluster) + top_exp_indices
            
            final_weights.append(combined_weights)
            final_indices.append(global_exp_indices)
            
        # Concatenate results from all selected clusters
        routing_weights = torch.cat(final_weights, dim=-1) # (N, top_c * top_e)
        expert_indices = torch.cat(final_indices, dim=-1) # (N, top_c * top_e)
        
        # Re-normalize weights so they sum to 1
        routing_weights = routing_weights / routing_weights.sum(dim=-1, keepdim=True)
        
        return routing_weights, expert_indices
