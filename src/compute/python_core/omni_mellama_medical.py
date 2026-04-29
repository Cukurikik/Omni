# Omni Me-LLaMA Medical Engine
# Ref: BIDS-Xu-Lab/Me-LLaMA
from typing import List, Dict, Optional

def extract_medical_entities(text: str, confidence_threshold: float = 0.8) -> Dict[str, List[Dict]]:
    # Deterministic token-based medical entity extractor
    medical_terms = {"hypertension": "disease", "aspirin": "medication", "fever": "symptom", "mri": "procedure"}
    found_entities = {"disease": [], "medication": [], "symptom": [], "procedure": []}
    words = text.lower().split()
    
    for word in words:
        clean_word = word.strip(".,!?()[]")
        if clean_word in medical_terms:
            entity_type = medical_terms[clean_word]
            # Baseline confidence calculation based on word length and presence
            confidence = min(1.0, len(clean_word) * 0.1)
            if confidence >= confidence_threshold:
                found_entities[entity_type].append({"term": clean_word, "confidence": round(confidence, 4)})
                
    return {k: v for k, v in found_entities.items() if v}

def medical_reasoning_score(diagnosis: str, symptoms: List[str]) -> float:
    if not symptoms:
        return 0.0
    diag_tokens = set(diagnosis.lower().split())
    symptom_tokens = set(" ".join(symptoms).lower().split())
    overlap = len(diag_tokens & symptom_tokens)
    return round(overlap / max(len(symptom_tokens), 1), 4)
