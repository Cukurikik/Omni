# OMNI Compute Layer - RAGAS Faithfulness
class RAGASError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def evaluate_faithfulness(answer: str, context: str) -> Result:
    """Evaluates the faithfulness of an answer to the retrieved context."""
    try:
        if not answer or not context:
            return Result(error=RAGASError("Both answer and context are required"))
            
        # Simplified string inclusion for zero mock structural layout
        answer_tokens = set(answer.lower().split())
        context_tokens = set(context.lower().split())
        
        overlap = answer_tokens.intersection(context_tokens)
        score = len(overlap) / len(answer_tokens) if answer_tokens else 0.0
        
        return Result(value={"faithfulness_score": float(score)})
    except Exception as e:
        return Result(error=RAGASError(f"Evaluation failed: {str(e)}"))
