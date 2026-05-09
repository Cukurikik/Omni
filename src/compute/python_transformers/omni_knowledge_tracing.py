"""OMNI Compute — Last Query Transformer RNN for Knowledge Tracing"""
import logging
from typing import List, Dict, Tuple
import math

logger = logging.getLogger("omni.knowledge_tracing")

class KnowledgeInteraction:
    def __init__(self, exercise_id: int, is_correct: bool, timestamp: int):
        self.exercise_id = exercise_id
        self.is_correct = is_correct
        self.timestamp = timestamp

class LastQueryTransformerRNN:
    """
    Implements Knowledge Tracing using Transformer + RNN.
    Predicts the probability of a student answering the *next* exercise correctly,
    based on their historical sequence of interactions.
    """
    def __init__(self, num_exercises: int = 10000, hidden_dim: int = 256):
        self.num_exercises = num_exercises
        self.hidden_dim = hidden_dim
        logger.info(f"Initialized Knowledge Tracing engine for {num_exercises} exercises")

    def _embed_interaction(self, interaction: KnowledgeInteraction) -> List[float]:
        """Embeds exercise ID and correctness into a combined feature vector."""
        # Simulated embedding
        base_val = (interaction.exercise_id % 100) / 100.0
        correct_multiplier = 1.0 if interaction.is_correct else -1.0
        
        return [base_val * correct_multiplier * (1.0 / (i+1)) for i in range(self.hidden_dim)]

    def _rnn_step(self, hidden_state: List[float], input_vec: List[float]) -> List[float]:
        """Simulates an LSTM/GRU step."""
        return [math.tanh(h + i) for h, i in zip(hidden_state, input_vec)]

    def _attention(self, query: List[float], keys: List[List[float]], values: List[List[float]]) -> List[float]:
        """Last Query Attention: attention from the last interaction to all previous ones."""
        if not keys:
            return query
            
        scores = []
        for k in keys:
            score = sum(q * kv for q, kv in zip(query, k)) / math.sqrt(self.hidden_dim)
            scores.append(score)
            
        max_s = max(scores)
        exp_s = [math.exp(s - max_s) for s in scores]
        sum_exp = sum(exp_s)
        attn_weights = [e / sum_exp for e in exp_s]
        
        context = [0.0] * self.hidden_dim
        for i, weight in enumerate(attn_weights):
            context = [c + weight * v for c, v in zip(context, values[i])]
            
        return context

    def predict_next(self, history: List[KnowledgeInteraction], target_exercise_id: int) -> float:
        """Predicts probability of answering target_exercise_id correctly."""
        if not history:
            return 0.5 # Unknown
            
        # 1. Embed History
        embedded_seq = [self._embed_interaction(ix) for ix in history]
        
        # 2. RNN Encoding
        rnn_states = []
        curr_state = [0.0] * self.hidden_dim
        for emb in embedded_seq:
            curr_state = self._rnn_step(curr_state, emb)
            rnn_states.append(curr_state)
            
        # 3. Last Query Attention (Transformer part)
        # Query is the target exercise embedding
        target_mock_ix = KnowledgeInteraction(target_exercise_id, True, 0)
        query = self._embed_interaction(target_mock_ix)
        
        context_vec = self._attention(query, keys=rnn_states, values=rnn_states)
        
        # 4. Prediction
        logit = sum(c * q for c, q in zip(context_vec, query))
        prob = 1.0 / (1.0 + math.exp(-max(min(logit, 20.0), -20.0)))
        return prob
