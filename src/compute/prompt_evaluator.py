# OMNI Compute Layer - Prompt Evaluator
class PromptError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def evaluate_prompt_complexity(prompt_text: str) -> Result:
    """Evaluates the structural complexity of a prompt for Promptdesk."""
    try:
        if not prompt_text:
            return Result(error=PromptError("Prompt text is required"))
            
        # Analyze parameters, variables, and length
        variables = prompt_text.count("{{")
        length = len(prompt_text)
        complexity_score = (variables * 10.0) + (length / 100.0)
        
        return Result(value={"score": float(complexity_score), "variables_detected": variables})
    except Exception as e:
        return Result(error=PromptError(f"Evaluation failed: {str(e)}"))
