"""
OMNI Compute — EHR Foundation Model Engine (Odyssey-inspired)
Medical EHR transformer with clinical event tokenization and forecasting.
"""
import logging, hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("omni.ehr")

@dataclass
class ClinicalEvent:
    code: str; code_system: str = "ICD10"; timestamp: float = 0.0
    value: Optional[float] = None; unit: str = ""
    visit_id: str = ""; event_type: str = "diagnosis"

@dataclass
class PatientTimeline:
    patient_id: str; events: List[ClinicalEvent] = field(default_factory=list)
    demographics: Dict = field(default_factory=dict)
    def sorted_events(self) -> List[ClinicalEvent]:
        return sorted(self.events, key=lambda e: e.timestamp)
    def num_visits(self) -> int:
        return len(set(e.visit_id for e in self.events if e.visit_id))

@dataclass
class EHRModelConfig:
    vocab_size: int = 50000; embed_dim: int = 256; num_heads: int = 8
    num_layers: int = 6; max_events: int = 2048; dropout: float = 0.1
    use_time_embedding: bool = True; use_visit_embedding: bool = True
    num_event_types: int = 20; num_age_buckets: int = 120

class EHRTokenizer:
    """Convert clinical events to token sequences."""
    def __init__(self, vocab_size: int = 50000):
        self.code_to_id: Dict[str, int] = {"[PAD]": 0, "[CLS]": 1, "[SEP]": 2, "[MASK]": 3}
        self.id_to_code: Dict[int, str] = {v: k for k, v in self.code_to_id.items()}
        self.next_id = 4; self.vocab_size = vocab_size
    def encode_event(self, event: ClinicalEvent) -> int:
        key = f"{event.code_system}:{event.code}"
        if key not in self.code_to_id:
            if self.next_id >= self.vocab_size: return hash(key) % self.vocab_size
            self.code_to_id[key] = self.next_id
            self.id_to_code[self.next_id] = key
            self.next_id += 1
        return self.code_to_id[key]
    def encode_timeline(self, timeline: PatientTimeline) -> Dict:
        events = timeline.sorted_events()
        tokens = [self.code_to_id["[CLS]"]]
        timestamps = [0.0]
        event_types = [0]
        for e in events:
            tokens.append(self.encode_event(e))
            timestamps.append(e.timestamp)
            event_types.append(hash(e.event_type) % 20)
        return {"token_ids": tokens, "timestamps": timestamps, "event_types": event_types,
                "patient_id": timeline.patient_id, "length": len(tokens)}
    @property
    def vocab_used(self) -> int: return self.next_id

class OmniEHREngine:
    """EHR foundation model engine for clinical event prediction."""
    def __init__(self, config: EHRModelConfig):
        self.config = config; self.tokenizer = EHRTokenizer(config.vocab_size)
    def preprocess_cohort(self, patients: List[PatientTimeline]) -> List[Dict]:
        return [self.tokenizer.encode_timeline(p) for p in patients]
    def create_forecasting_targets(self, encoded: Dict, forecast_window: int = 5) -> Dict:
        tokens = encoded["token_ids"]
        if len(tokens) <= forecast_window:
            return {"input": tokens, "target": [], "valid": False}
        return {"input": tokens[:-forecast_window], "target": tokens[-forecast_window:], "valid": True}
    def get_stats(self) -> Dict:
        return {"vocab_used": self.tokenizer.vocab_used, "config": vars(self.config)}
