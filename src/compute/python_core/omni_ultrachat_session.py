from typing import List, Dict

class OmniUltraChatSession:
    """OMNI Compute Layer: UltraChat Diversified Dialogue Generator"""
    
    def __init__(self, diversity_penalty: float = 0.2):
        self.diversity_penalty = diversity_penalty

    def select_next_persona(self, previous_personas: List[str], available: List[str]) -> str:
        if not available:
            return "default"
            
        # Deterministic persona selection avoiding recent ones
        for p in available:
            if p not in previous_personas[-3:]:
                return p
                
        return available[0]
