from typing import List

class OmniRepoCodRetriever:
    """OMNI Compute Layer: RepoCod Repository-Level Code Retriever"""
    
    def __init__(self, max_files: int = 10):
        self.max_files = max_files

    def extract_context(self, query: str, repo_files: dict[str, str]) -> List[str]:
        if not query or not repo_files:
            return []
            
        # Deterministic dummy retrieval based on filename overlap
        query_terms = set(query.lower().split())
        matched_files = []
        
        for fname, content in repo_files.items():
            if any(term in fname.lower() for term in query_terms):
                matched_files.append(fname)
                
        return matched_files[:self.max_files]
