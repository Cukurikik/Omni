# Omni Repilot Patch Generator
# Compute: Automated program repair with LLM + completion engine.
# Ref: ise-uiuc/Repilot — ESEC/FSE 2023
import hashlib
from typing import Dict, List

def compute_patch_score(original: str, patched: str, test_pass: bool) -> Dict:
    dist = sum(1 for a, b in zip(original, patched) if a != b)
    dist += abs(len(original) - len(patched))
    return {"distance": dist, "passes_test": test_pass,
            "score": round((1.0 / (1.0 + dist)) * (1.0 if test_pass else 0.1), 6)}

def rank_patches(patches: List[Dict]) -> List[Dict]:
    return sorted(patches, key=lambda p: p.get("score", 0), reverse=True)
