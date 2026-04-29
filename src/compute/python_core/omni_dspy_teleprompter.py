from typing import List

class OmniDSPyTeleprompter:
    """OMNI Compute Layer: DSPy Declarative Prompt Optimizer"""
    
    def __init__(self, metric_threshold: float = 0.8):
        self.threshold = metric_threshold

    def bootstrap_few_shot(self, examples: List[str], eval_metric: float) -> str:
        if not examples:
            return "No examples provided."
            
        base_prompt = "Here are examples:\\n" + "\\n".join(examples)
        
        if eval_metric < self.threshold:
            # Optimize prompt by adding strict instructions
            base_prompt = "PAY ATTENTION TO FORMAT.\\n" + base_prompt
            
        return base_prompt
