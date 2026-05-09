"""OMNI Compute — CEHR-BERT Temporal Engine"""
import logging, math
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("omni.cehrbert")

@dataclass
class ClinicalEvent:
    concept_id: int
    timestamp: int
    age_in_months: int
    visit_segment: int

@dataclass
class CEHRConfig:
    vocab_size: int = 50000
    hidden_size: int = 768
    num_hidden_layers: int = 12
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    max_seq_length: int = 512
    time_embeddings_size: int = 64

class TemporalEmbedding:
    """Embeds time intervals between clinical events."""
    def __init__(self, config: CEHRConfig):
        self.config = config
        # In production, these are learnable weights
        self.time_emb_weights = [[0.01 * i * j for j in range(config.time_embeddings_size)] for i in range(1000)]
        self.age_emb_weights = [[0.01 * i * j for j in range(config.hidden_size)] for i in range(1200)] # 100 years in months
        self.visit_emb_weights = [[0.01 * i * j for j in range(config.hidden_size)] for i in range(100)]
        self.concept_emb_weights = [[0.01 * (i % 10) for j in range(config.hidden_size)] for i in range(config.vocab_size)]

    def embed(self, events: List[ClinicalEvent]) -> List[List[float]]:
        embeddings = []
        for i, event in enumerate(events):
            # 1. Concept embedding
            emb = list(self.concept_emb_weights[event.concept_id])
            
            # 2. Age embedding
            age_idx = min(event.age_in_months, 1199)
            age_emb = self.age_emb_weights[age_idx]
            emb = [e + a for e, a in zip(emb, age_emb)]
            
            # 3. Visit segment embedding
            visit_idx = min(event.visit_segment, 99)
            visit_emb = self.visit_emb_weights[visit_idx]
            emb = [e + v for e, v in zip(emb, visit_emb)]
            
            # 4. Temporal difference embedding (Time to previous event)
            if i > 0:
                time_diff = event.timestamp - events[i-1].timestamp
                time_idx = min(time_diff // (24 * 3600), 999) # Days
                time_emb = self.time_emb_weights[time_idx]
                # Project time_emb to hidden_size (simplified pad)
                time_emb_proj = time_emb * (self.config.hidden_size // self.config.time_embeddings_size)
                emb = [e + t for e, t in zip(emb, time_emb_proj)]
            
            embeddings.append(emb)
        return embeddings

class CEHRBertEngine:
    """CEHR-BERT: Incorporating temporal information from EHR data."""
    def __init__(self, config: CEHRConfig):
        self.config = config
        self.embedding = TemporalEmbedding(config)
        logger.info(f"Initialized CEHR-BERT with hidden_size={config.hidden_size}")

    def predict_disease_risk(self, patient_history: List[ClinicalEvent], target_disease_concept: int) -> float:
        """Predict probability of developing target disease in next 6 months."""
        if not patient_history:
            return 0.0
            
        # 1. Embed history with temporal and demographic context
        embedded_seq = self.embedding.embed(patient_history)
        
        # 2. Self-Attention Pass (Simulated Transformer Encoder)
        seq_len = len(embedded_seq)
        context_vector = [0.0] * self.config.hidden_size
        for emb in embedded_seq:
            context_vector = [c + e/seq_len for c, e in zip(context_vector, emb)]
            
        # 3. Prediction Head
        # Dot product with target disease concept vector
        target_vec = self.embedding.concept_emb_weights[target_disease_concept]
        logit = sum(c * t for c, t in zip(context_vector, target_vec))
        
        # Sigmoid activation
        probability = 1.0 / (1.0 + math.exp(-max(min(logit, 20.0), -20.0)))
        return probability

    def extract_patient_representation(self, patient_history: List[ClinicalEvent]) -> List[float]:
        """Extract CLS token equivalent representation for downstream tasks."""
        if not patient_history:
            return [0.0] * self.config.hidden_size
        embedded_seq = self.embedding.embed(patient_history)
        # Mean pooling over sequence for representation
        seq_len = len(embedded_seq)
        return [sum(emb[i] for emb in embedded_seq) / seq_len for i in range(self.config.hidden_size)]
