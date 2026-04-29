# Omni Scratchpad Reasoning Framework
# Ref: para-droid-ai/scratchpad — MIT
from typing import List, Dict
def decompose_intent(user_input: str) -> Dict:
    words = user_input.split()
    return {"raw": user_input, "n_tokens": len(words), "has_question": "?" in user_input,
            "complexity": "high" if len(words) > 30 else "medium" if len(words) > 10 else "low"}
def build_scratchpad(steps: List[str]) -> str:
    return "\n".join(f"Step {i+1}: {s}" for i, s in enumerate(steps))
def calibrate_response(response: str, user_context: Dict) -> Dict:
    detail = user_context.get("detail_level", "medium")
    if detail == "low": response = " ".join(response.split()[:50])
    return {"response": response, "detail_level": detail, "word_count": len(response.split())}
