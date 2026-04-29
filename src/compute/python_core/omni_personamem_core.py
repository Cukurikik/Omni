from typing import List, Dict, Optional

class OmniPersonaMemCore:
    """OMNI Compute Layer: PersonaMem Engine (Zero-Mock)"""
    
    def __init__(self, memory_limit: int = 100):
        self.limit = memory_limit
        self.memory_store: List[Dict[str, str]] = []

    def update_persona(self, user_id: str, fact: str) -> bool:
        if len(self.memory_store) >= self.limit:
            self.memory_store.pop(0) # LRU evict
            
        # Deterministic deduplication
        for entry in self.memory_store:
            if entry.get("user") == user_id and entry.get("fact") == fact:
                return False
                
        self.memory_store.append({"user": user_id, "fact": fact})
        return True
        
    def retrieve_persona(self, user_id: str) -> List[str]:
        return [entry["fact"] for entry in self.memory_store if entry.get("user") == user_id]
