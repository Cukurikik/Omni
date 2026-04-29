from typing import List, Dict

class OmniMoERouter:
    """OMNI Compute Layer: Mixture of Experts Router (Zero-Mock)"""
    
    def __init__(self, expert_capacities: Dict[str, int]):
        self.capacities = expert_capacities
        self.current_load = {k: 0 for k in expert_capacities}

    def route_tokens(self, tokens: List[str], top_k: int = 2) -> Dict[str, List[str]]:
        if top_k <= 0 or top_k > len(self.capacities):
            raise ValueError("Invalid top_k value.")
            
        routing_assignment = {k: [] for k in self.capacities}
        
        for idx, token in enumerate(tokens):
            # Deterministic pseudo-hash for routing
            hash_val = hash(token)
            sorted_experts = sorted(self.capacities.keys(), key=lambda e: (hash_val ^ hash(e)))
            
            assigned = 0
            for expert in sorted_experts:
                if self.current_load[expert] < self.capacities[expert]:
                    routing_assignment[expert].append(token)
                    self.current_load[expert] += 1
                    assigned += 1
                    if assigned == top_k:
                        break
        return routing_assignment
