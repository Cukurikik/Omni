from typing import List, Dict

class OmniMLMMEvaluator:
    """OMNI Compute Layer: MLMM Multilingual Evaluator (Zero-Mock)"""
    
    def __init__(self, languages: List[str]):
        self.langs = languages

    def evaluate_cross_lingual(self, preds: Dict[str, str], truth: Dict[str, str]) -> Dict[str, float]:
        scores = {}
        for lang in self.langs:
            p = preds.get(lang, "").strip()
            t = truth.get(lang, "").strip()
            
            if not p or not t:
                scores[lang] = 0.0
                continue
                
            # Exact match check
            if p == t:
                scores[lang] = 1.0
            else:
                scores[lang] = 0.0
                
        return scores
