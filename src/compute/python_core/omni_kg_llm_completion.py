# Omni KG-LLM Knowledge Graph Completion Engine
# Ref: yao8839836/kg-llm
from typing import List, Tuple, Dict

def predict_tail_entity(head: str, relation: str, candidate_tails: List[str], llm_scores: List[float]) -> Dict:
    """Select best tail entity for knowledge graph completion based on LLM plausibility scores."""
    if not candidate_tails or len(candidate_tails) != len(llm_scores):
        return {"predicted_tail": None, "confidence": 0.0}
        
    scored = list(zip(candidate_tails, llm_scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    
    best_tail, highest_score = scored[0]
    
    # Normalize confidence using softmax approximation
    exp_sum = sum(2.718 ** s for s in llm_scores)
    confidence = (2.718 ** highest_score) / max(exp_sum, 1e-8)
    
    return {
        "triple": (head, relation, best_tail),
        "confidence": round(confidence, 4)
    }

def kg_completion_mrr(predictions: List[List[str]], ground_truths: List[str]) -> float:
    """Calculate Mean Reciprocal Rank (MRR) for KG completion predictions."""
    if not predictions or not ground_truths or len(predictions) != len(ground_truths):
        return 0.0
        
    rr_sum = 0.0
    for preds, truth in zip(predictions, ground_truths):
        try:
            rank = preds.index(truth) + 1
            rr_sum += 1.0 / rank
        except ValueError:
            pass # Truth not in predictions
            
    return round(rr_sum / len(ground_truths), 4)
