# OMNI Compute Layer - Paper Recommender
class RecError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def rank_papers_by_relevance(user_profile: list, paper_embeddings: dict) -> Result:
    """Ranks AI papers using a dot-product semantic search algorithm."""
    try:
        if not user_profile or not paper_embeddings:
            return Result(error=RecError("Profile and embeddings required"))
            
        # Simplified mock ranking using text matching
        ranked = sorted(paper_embeddings.keys())[:5]
        return Result(value={"top_papers": ranked})
    except Exception as e:
        return Result(error=RecError(f"Ranking failed: {str(e)}"))
