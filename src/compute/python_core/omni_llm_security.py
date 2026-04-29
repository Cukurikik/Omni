# Omni LLM Security Hardening Engine
# Ref: forcesunseen/llm-hackers-handbook
from typing import List, Dict
INJECTION_PATTERNS = ["ignore previous", "disregard instructions", "system prompt", "jailbreak",
                      "do anything now", "pretend you are", "bypass", "override"]
def detect_injection(text: str) -> Dict:
    t = text.lower()
    found = [p for p in INJECTION_PATTERNS if p in t]
    return {"is_injection": len(found) > 0, "patterns": found, "risk": round(len(found)/len(INJECTION_PATTERNS),4)}
def sanitize_input(text: str) -> str:
    for p in INJECTION_PATTERNS: text = text.replace(p, "[FILTERED]")
    return text
def output_guard(response: str, forbidden: List[str]) -> Dict:
    violations = [f for f in forbidden if f.lower() in response.lower()]
    return {"safe": len(violations)==0, "violations": violations}
