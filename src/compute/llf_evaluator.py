# OMNI Compute Layer - LLF Evaluator
import numpy as np

class LLFError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def evaluate_feedback(responses: list, feedback: list) -> Result:
    """Evaluates learning agents based on language feedback."""
    try:
        if len(responses) != len(feedback):
            return Result(error=LLFError("Mismatched responses and feedback counts"))
            
        # Basic proxy for learning quality
        positive_keywords = ['correct', 'good', 'excellent', 'yes']
        scores = []
        
        for fb in feedback:
            score = 1.0 if any(k in fb.lower() for k in positive_keywords) else 0.0
            scores.append(score)
            
        return Result(value={"mean_score": float(np.mean(scores))})
    except Exception as e:
        return Result(error=LLFError(f"Evaluation failed: {str(e)}"))
