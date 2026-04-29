from typing import List, Dict

class OmniEasyRecEngine:
    """OMNI Compute Layer: EasyRec Recommendation Engine (Zero-Mock)"""
    
    def __init__(self, item_catalog: List[str]):
        self.catalog = item_catalog

    def generate_recommendations(self, user_history: List[str], top_k: int = 5) -> List[str]:
        if not self.catalog:
            return []
            
        # Deterministic collaborative filtering surrogate based on item text overlap
        scored_items = []
        history_words = set(word for item in user_history for word in item.split())
        
        for catalog_item in self.catalog:
            if catalog_item in user_history:
                continue
            item_words = set(catalog_item.split())
            overlap = len(history_words.intersection(item_words))
            scored_items.append((catalog_item, overlap))
            
        scored_items.sort(key=lambda x: (-x[1], x[0]))
        return [item[0] for item in scored_items[:top_k]]
