# Omni Sentiment Reasoning Engine
# Ref: leduckhai/Sentiment-Reasoning (Healthcare)
import math
from typing import List, Dict

def compute_sentiment_polarity(text: str, positive_lexicon: set, negative_lexicon: set) -> float:
    words = text.lower().split()
    pos_count = sum(1 for w in words if w in positive_lexicon)
    neg_count = sum(1 for w in words if w in negative_lexicon)
    
    total = pos_count + neg_count
    if total == 0:
        return 0.0
    return round((pos_count - neg_count) / total, 4)

def healthcare_sentiment_analysis(clinical_notes: List[str]) -> Dict[str, float]:
    pos_lex = {"stable", "improving", "recovered", "normal", "healthy", "negative"} # 'negative' test result is often good
    neg_lex = {"pain", "fever", "critical", "worse", "abnormal", "positive"} # 'positive' test result can be bad
    
    scores = [compute_sentiment_polarity(note, pos_lex, neg_lex) for note in clinical_notes]
    
    if not scores:
        return {"mean_sentiment": 0.0, "variance": 0.0, "critical_cases": 0.0}
        
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    critical = sum(1 for s in scores if s < -0.5)
    
    return {
        "mean_sentiment": round(mean, 4),
        "variance": round(variance, 4),
        "critical_cases": float(critical)
    }
