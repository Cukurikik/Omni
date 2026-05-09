"""OMNI Compute — Intent Classification & Slot Filling"""
import logging
from typing import List, Dict, Tuple
import math

logger = logging.getLogger("omni.intent_classifier")

class IntentClassifier:
    """
    Joint Intent Classification and Slot Filling using Transformers.
    Reference: iclassifier (BERT/CNN/DenseNet for NLP).
    """
    def __init__(self, intents: List[str], slots: List[str], hidden_size: int = 768):
        self.intents = intents
        self.slots = slots
        self.hidden_size = hidden_size
        logger.info(f"Initialized Intent Classifier with {len(intents)} intents and {len(slots)} slots")

    def _simulate_bert_encoder(self, tokens: List[str]) -> Tuple[List[float], List[List[float]]]:
        """Simulate CLS token and token-level embeddings."""
        cls_emb = [sum(ord(c) for c in "".join(tokens)) * 0.01 / self.hidden_size for _ in range(self.hidden_size)]
        
        token_embs = []
        for t in tokens:
            t_emb = [ord(c) * 0.05 for c in t][:self.hidden_size]
            if len(t_emb) < self.hidden_size:
                t_emb.extend([0.0] * (self.hidden_size - len(t_emb)))
            token_embs.append(t_emb)
            
        return cls_emb, token_embs

    def predict(self, text: str) -> Dict[str, Any]:
        """Predict intent and extract slots from text."""
        tokens = text.split()
        cls_emb, token_embs = self._simulate_bert_encoder(tokens)
        
        # 1. Intent Classification (from CLS token)
        intent_scores = [sum(cls_emb) * (i+1) % 10.0 for i in range(len(self.intents))]
        max_i_score = max(intent_scores)
        exp_i = [math.exp(s - max_i_score) for s in intent_scores]
        sum_exp_i = sum(exp_i)
        intent_probs = [e / sum_exp_i for e in exp_i]
        
        predicted_intent = self.intents[intent_probs.index(max(intent_probs))]
        
        # 2. Slot Filling (Token level CRF/Linear simulation)
        extracted_slots = []
        for i, token in enumerate(tokens):
            t_score = sum(token_embs[i])
            # Simulated heuristic
            slot_idx = int(t_score) % len(self.slots)
            slot_label = self.slots[slot_idx]
            if slot_label != "O": # 'O' represents outside/no slot
                extracted_slots.append({"token": token, "slot": slot_label})
                
        return {
            "text": text,
            "intent": predicted_intent,
            "intent_confidence": round(max(intent_probs), 4),
            "slots": extracted_slots
        }
