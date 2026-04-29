# Omni Aria Voice Assistant
# Ref: lef-fan/aria — AGPL-3.0
from typing import Dict
def classify_intent(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["weather","temperature","forecast"]): return "weather"
    if any(w in t for w in ["remind","alarm","timer"]): return "reminder"
    if any(w in t for w in ["play","music","song"]): return "media"
    if any(w in t for w in ["search","find","look"]): return "search"
    return "general"
def compute_vad_energy(samples: list, threshold: float = 0.02) -> Dict:
    if not samples: return {"active": False, "energy": 0.0}
    energy = sum(s*s for s in samples) / len(samples)
    return {"active": energy > threshold, "energy": round(energy, 8)}
