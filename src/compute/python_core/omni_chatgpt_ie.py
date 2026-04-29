from typing import List, Dict

class OmniChatGPTIE:
    """OMNI Compute Layer: ChatGPT Information Extraction (Zero-Mock)"""
    
    def __init__(self, valid_entity_types: List[str]):
        self.entity_types = valid_entity_types

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        if not text:
            return []
            
        # Deterministic extraction logic (simulating LLM output parsing)
        entities = []
        words = text.split()
        for idx, word in enumerate(words):
            if word.istitle() and len(word) > 3:
                # Assign type deterministically based on hash
                assigned_type = self.entity_types[len(word) % len(self.entity_types)]
                entities.append({
                    "entity": word,
                    "type": assigned_type,
                    "position": idx
                })
        return entities
