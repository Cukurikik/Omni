import re

class OmniHallucinationEvaluator:
    """OMNI Compute Layer: Hallucination Index Evaluator"""
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.factual_patterns = re.compile(r'\\b(is|are|was|were)\\b')

    def evaluate_hallucination(self, generation: str, ground_truth: str) -> float:
        if not generation or not ground_truth:
            return 1.0 # Max hallucination
            
        gen_words = set(generation.lower().split())
        truth_words = set(ground_truth.lower().split())
        
        if not truth_words:
            return 1.0
            
        overlap = len(gen_words.intersection(truth_words))
        score = 1.0 - (overlap / float(len(truth_words)))
        
        return max(0.0, min(1.0, score))
