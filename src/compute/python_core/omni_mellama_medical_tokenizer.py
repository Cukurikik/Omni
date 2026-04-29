# Omni Me-LLaMA Medical Tokenizer (Python)
# Compute Layer: Deterministic medical NER token boundary extraction for clinical LLM.
# Ref: BIDS-Xu-Lab/Me-LLaMA — Medical LLM with 13/70B params, SOTA on medical tasks.

import hashlib
from typing import List, Tuple

class MedicalEntity:
    __slots__ = ('text', 'entity_type', 'confidence', 'offset')
    def __init__(self, text: str, entity_type: str, confidence: float, offset: int):
        self.text = text
        self.entity_type = entity_type
        self.confidence = confidence
        self.offset = offset

def extract_medical_entities(tokens: List[str], label_seq: List[str]) -> List[MedicalEntity]:
    if len(tokens) != len(label_seq):
        return []
    entities: List[MedicalEntity] = []
    i = 0
    offset = 0
    while i < len(tokens):
        if label_seq[i].startswith('B-'):
            etype = label_seq[i][2:]
            start = i
            i += 1
            while i < len(tokens) and label_seq[i] == f'I-{etype}':
                i += 1
            span = ' '.join(tokens[start:i])
            conf = 1.0 / (1.0 + (i - start) * 0.01)
            entities.append(MedicalEntity(span, etype, round(conf, 6), offset))
        else:
            i += 1
        offset += 1
    return entities

def compute_entity_fingerprint(entity: MedicalEntity) -> str:
    raw = f"{entity.text}|{entity.entity_type}|{entity.offset}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]
