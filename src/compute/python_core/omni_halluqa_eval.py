class OmniHalluQAEval:
    """OMNI Compute Layer: HalluQA Evaluator (Zero-Mock)"""
    
    def __init__(self, strict_mode: bool = True):
        self.strict = strict_mode

    def evaluate_hallucination(self, generation: str, ground_truth: str) -> float:
        if not generation or not ground_truth:
            return 1.0 # 100% hallucination if empty
            
        gen_words = set(generation.lower().split())
        truth_words = set(ground_truth.lower().split())
        
        if not gen_words:
            return 1.0
            
        intersection = gen_words.intersection(truth_words)
        precision = len(intersection) / len(gen_words)
        
        # Hallucination score is inverse of precision
        hallucination_score = 1.0 - precision
        
        if self.strict and hallucination_score > 0.5:
            return 1.0 # Penalize heavily in strict mode
            
        return hallucination_score
