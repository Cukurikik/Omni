from typing import Dict, Any

class OmniGraphTranslatorAligner:
    """OMNI Compute Layer: GraphTranslator Modality Alignment"""
    
    def __init__(self, node_dim: int = 128):
        self.node_dim = node_dim

    def graph_to_text(self, adjacency_list: Dict[str, list[str]]) -> str:
        if not adjacency_list:
            return "Empty graph."
            
        # Deterministic graph serialization
        sentences = []
        for node, neighbors in adjacency_list.items():
            if neighbors:
                sentences.append(f"Node {node} is connected to {', '.join(neighbors)}.")
            else:
                sentences.append(f"Node {node} has no connections.")
                
        return " ".join(sentences)
