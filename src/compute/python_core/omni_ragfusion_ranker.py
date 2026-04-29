from typing import List, Dict

class OmniRAGFusionRanker:
    """OMNI Compute Layer: RAG-Fusion Reciprocal Rank Fusion Engine"""
    
    def __init__(self, k: int = 60):
        self.k = k

    def rrf_score(self, ranked_lists: List[List[str]]) -> List[str]:
        scores: Dict[str, float] = {}
        
        for r_list in ranked_lists:
            for rank, doc_id in enumerate(r_list):
                if doc_id not in scores:
                    scores[doc_id] = 0.0
                scores[doc_id] += 1.0 / (self.k + rank + 1)
                
        # Sort by score descending
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [doc[0] for doc in sorted_docs]
