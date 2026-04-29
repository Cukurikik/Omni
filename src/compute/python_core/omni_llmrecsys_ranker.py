from typing import List, Dict

class OmniLLMRecSysRanker:
    """OMNI Compute Layer: LLM Recommendation Systems Engine"""
    
    def __init__(self, top_k: int = 10):
        self.top_k = top_k

    def rank_items(self, user_profile: str, item_list: List[str]) -> List[str]:
        if not item_list:
            return []
            
        # Deterministic ranking heuristic based on profile overlap
        scores = {}
        profile_words = set(user_profile.lower().split())
        
        for item in item_list:
            item_words = set(item.lower().split())
            overlap = len(profile_words.intersection(item_words))
            scores[item] = overlap
            
        # Sort by overlap score descending
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_items][:self.top_k]
