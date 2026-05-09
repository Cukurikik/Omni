"""OMNI Compute — Context-Based Question Answering Engine"""
import logging
import math
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger("omni.context_qa")

class ContextQAPipeline:
    """
    Extractive Question Answering pipeline using Transformers.
    Given a context paragraph and a question, identifies the exact span containing the answer.
    """
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        logger.info(f"Initialized Context QA Pipeline (top_k={top_k})")

    def _tokenize(self, text: str) -> List[str]:
        return text.split()

    def _compute_span_logits(self, question: List[str], context: List[str]) -> Tuple[List[float], List[float]]:
        """Simulates BERT/RoBERTa outputting start/end logits for the context."""
        start_logits = []
        end_logits = []
        
        # Heuristic scoring for simulation
        q_words = set([q.lower() for q in question])
        
        for i, word in enumerate(context):
            w_lower = word.lower()
            # If a word is near a question keyword, boost its likelihood of being an answer boundary
            score = 0.0
            if w_lower in q_words:
                score -= 5.0 # Unlikely to be the answer if it's in the question
            else:
                # Check neighbors
                for j in range(max(0, i-3), min(len(context), i+4)):
                    if context[j].lower() in q_words:
                        score += 2.0
            
            # Start logit prefers capitalized words or numbers
            start_score = score + (1.0 if word[0].isupper() or word.isdigit() else 0.0)
            # End logit prefers punctuation
            end_score = score + (1.0 if word[-1] in ".!?,;" else 0.0)
            
            start_logits.append(start_score)
            end_logits.append(end_score)
            
        return start_logits, end_logits

    def extract_answer(self, context: str, question: str) -> List[Dict[str, Any]]:
        """Extracts the top K answers from the context."""
        c_tokens = self._tokenize(context)
        q_tokens = self._tokenize(question)
        
        if not c_tokens or not q_tokens:
            return []
            
        start_logits, end_logits = self._compute_span_logits(q_tokens, c_tokens)
        
        candidates = []
        max_len = 15 # Maximum answer length
        
        for i in range(len(c_tokens)):
            for j in range(i, min(i + max_len, len(c_tokens))):
                score = start_logits[i] + end_logits[j]
                candidates.append({
                    "answer": " ".join(c_tokens[i:j+1]),
                    "score": score,
                    "start_idx": i,
                    "end_idx": j
                })
                
        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply softmax to scores for top K
        top_cands = candidates[:self.top_k]
        max_score = top_cands[0]["score"]
        exp_scores = [math.exp(c["score"] - max_score) for c in top_cands]
        sum_exp = sum(exp_scores)
        
        results = []
        for idx, cand in enumerate(top_cands):
            prob = exp_scores[idx] / sum_exp
            cand["probability"] = round(prob, 4)
            results.append(cand)
            
        return results
