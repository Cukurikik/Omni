from typing import Dict, Any, List, Set
from dataclasses import dataclass
import networkx as nx

# OMNI Chain-of-Image (CoI) Reasoning Engine
# Computational Layer
# Applies combinatorial logical routing over sequential image semantic graphs. 
# Zero language model mocking, operates strictly on pre-computed relational graphs.

@dataclass
class CoiResult:
    ok: bool
    path: List[str] = None
    confidence: float = 0.0
    error: str = None

class OmniCoiReasoningEngine:
    def __init__(self):
        self.logic_graph = nx.DiGraph()
        self.reasoning_paths_traced = 0

    def inject_image_semantic_node(self, node_id: str, semantic_vector: list, connections: Dict[str, float]):
        """
        Adds an image frame conceptually into the reasoning graph.
        connections is a dictionary mapping target_node_id -> semantic_similarity_weight (0.0 to 1.0).
        """
        self.logic_graph.add_node(node_id, vector=semantic_vector)
        for target, weight in connections.items():
            # In CoI, higher weight means stronger logic connection.
            # For shortest path compat, we convert weight to 'cost' inversely.
            cost = 1.0 - weight
            cost = max(cost, 0.01) # Prevent 0 cost loops
            self.logic_graph.add_edge(node_id, target, weight=cost, confidence=weight)

    def trace_chain_of_imagery(self, start_node: str, end_node: str) -> CoiResult:
        """
        Deduces the most logical sequential path bridging two visual concepts (nodes) using Dijkstra.
        """
        if start_node not in self.logic_graph or end_node not in self.logic_graph:
            return CoiResult(False, error="CoiError: Node coordinates missing from spatial graph.")
            
        self.reasoning_paths_traced += 1
        
        try:
            # Shortest path using inversed weights
            path = nx.dijkstra_path(self.logic_graph, start_node, end_node, weight='weight')
            
            # Calculate aggregate chain confidence mathematically (product of probabilities)
            chain_confidence = 1.0
            for i in range(len(path) - 1):
                edge_data = self.logic_graph.get_edge_data(path[i], path[i+1])
                chain_confidence *= edge_data.get('confidence', 0.5)
                
            return CoiResult(True, path=path, confidence=chain_confidence)
            
        except nx.NetworkXNoPath:
            return CoiResult(False, error="CoiError: No logical traversal path exists.")
        except Exception as e:
            return CoiResult(False, error=f"CoiError: Combinatorial engine fault: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniCoiReasoningEngine",
            "nodes_in_graph": self.logic_graph.number_of_nodes(),
            "edges_in_graph": self.logic_graph.number_of_edges(),
            "paths_traced": self.reasoning_paths_traced,
            "status": "Operational"
        }
