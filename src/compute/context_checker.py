# OMNI Compute Layer - Context Checker
class CheckError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def verify_rag_context_relevance(question: str, retrieved_context: list) -> Result:
    """Evaluates if the RAG context actually answers the query."""
    try:
        if not question or not retrieved_context:
            return Result(error=CheckError("Missing question or context"))
            
        combined = " ".join(retrieved_context).lower()
        question_keywords = set([w for w in question.lower().split() if len(w) > 3])
        
        match_count = sum(1 for kw in question_keywords if kw in combined)
        relevance_ratio = match_count / len(question_keywords) if question_keywords else 1.0
        
        return Result(value={"relevance_score": float(relevance_ratio), "is_hallucinating": relevance_ratio < 0.3})
    except Exception as e:
        return Result(error=CheckError(f"Check failed: {str(e)}"))
