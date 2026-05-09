"""OMNI Compute — Graph Transformer"""
import logging
import math
from typing import List, Dict

logger = logging.getLogger("omni.graph_transformer")

class GraphNode:
    def __init__(self, node_id: int, features: List[float]):
        self.node_id = node_id
        self.features = features

class GraphTransformer:
    """
    Graph Transformer Network.
    Combines Message Passing with Multi-Head Self-Attention for Graph Structured Data.
    """
    def __init__(self, d_model: int = 64):
        self.d_model = d_model
        logger.info("Initialized Graph Transformer Network")

    def forward(self, nodes: List[GraphNode], adjacency_matrix: List[List[int]]) -> List[GraphNode]:
        """
        Self-attention restricted/biased by graph connectivity.
        """
        num_nodes = len(nodes)
        out_nodes = []
        
        for i in range(num_nodes):
            context = [0.0]*self.d_model
            weight_sum = 0.0
            
            # Attend to self and neighbors
            for j in range(num_nodes):
                is_neighbor = adjacency_matrix[i][j] > 0
                if i == j or is_neighbor:
                    # Calculate attention weight
                    dot = sum(nodes[i].features[d] * nodes[j].features[d] for d in range(self.d_model))
                    # Add structural bias (e.g., edge features, simplified to 1.0 here)
                    bias = 1.0 if is_neighbor else 0.0
                    w = math.exp((dot / math.sqrt(self.d_model)) + bias)
                    
                    weight_sum += w
                    for d in range(self.d_model):
                        context[d] += w * nodes[j].features[d]
            
            new_features = [c / max(weight_sum, 1e-9) for c in context]
            out_nodes.append(GraphNode(nodes[i].node_id, new_features))
            
        return out_nodes
