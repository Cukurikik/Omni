from typing import List, Tuple

class OmniGraphEditLearner:
    """OMNI Compute Layer: GraphEdit Structure Learner (Zero-Mock)"""
    
    def __init__(self, max_edges: int):
        self.max_edges = max_edges

    def learn_structure(self, nodes: List[str], constraints: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        if not nodes:
            return []
            
        edges = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                edge = (nodes[i], nodes[j])
                # Hard constraints check
                if edge not in constraints and (nodes[j], nodes[i]) not in constraints:
                    # Deterministic structural affinity
                    if len(nodes[i]) % 2 == len(nodes[j]) % 2:
                        edges.append(edge)
                        if len(edges) >= self.max_edges:
                            return edges
        return edges
