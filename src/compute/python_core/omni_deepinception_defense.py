# Omni DeepInception Jailbreak Defense Engine
# Ref: tmlr-group/DeepInception — MIT
# Hypnotic nested-scene jailbreak detection and defense
import re
from typing import List, Dict

INCEPTION_MARKERS = [
    "create a story", "imagine a world", "in this fictional",
    "roleplay as", "pretend you are", "in a hypothetical",
    "write a screenplay", "as a character", "nested scenario",
    "layer 1", "layer 2", "scene within a scene"
]

HARMFUL_CATEGORIES = [
    "violence", "illegal", "weapon", "drug", "hack", "exploit",
    "steal", "attack", "bomb", "poison", "malware", "fraud"
]

def detect_inception_attack(prompt: str) -> Dict:
    """Detect DeepInception-style nested jailbreak attempts."""
    prompt_lower = prompt.lower()
    found_markers = [m for m in INCEPTION_MARKERS if m in prompt_lower]
    nesting_depth = sum(1 for m in ["layer", "scene", "level", "step"] if m in prompt_lower)
    harmful_flags = [c for c in HARMFUL_CATEGORIES if c in prompt_lower]
    risk_score = min(1.0, (len(found_markers) * 0.15 + nesting_depth * 0.1 + len(harmful_flags) * 0.2))
    return {
        "is_inception": len(found_markers) >= 2 and len(harmful_flags) >= 1,
        "risk_score": round(risk_score, 4),
        "nesting_depth": nesting_depth,
        "markers_found": found_markers,
        "harmful_flags": harmful_flags
    }

def defense_filter(prompt: str, threshold: float = 0.5) -> Dict:
    """Apply DeepInception defense filter."""
    analysis = detect_inception_attack(prompt)
    blocked = analysis["risk_score"] >= threshold
    return {"blocked": blocked, "analysis": analysis,
            "action": "BLOCK" if blocked else "ALLOW"}

def batch_defense_audit(prompts: List[str], threshold: float = 0.5) -> Dict:
    """Audit a batch of prompts for inception attacks."""
    results = [defense_filter(p, threshold) for p in prompts]
    blocked_count = sum(1 for r in results if r["blocked"])
    return {
        "total": len(prompts), "blocked": blocked_count,
        "allowed": len(prompts) - blocked_count,
        "block_rate": round(blocked_count / max(len(prompts), 1), 4)
    }

def extract_nested_layers(prompt: str) -> List[str]:
    """Extract nested narrative layers from an inception prompt."""
    layers = re.split(r'(?:layer|scene|level)\s*\d+', prompt, flags=re.IGNORECASE)
    return [l.strip() for l in layers if l.strip()]
