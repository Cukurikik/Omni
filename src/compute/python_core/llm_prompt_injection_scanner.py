import typing
from typing import Dict, Any

class LlmPromptInjectionScanner:
    """
    OMNI Framework - LLM Prompt Injection Scanner
    Detects malicious intents, system prompt overrides, and jailbreaks.
    """
    def __init__(self, sensitivity: float = 0.8):
        self.sensitivity = sensitivity

    def scan_prompt(self, prompt: str) -> Dict[str, Any]:
        """Scans the prompt for injection attacks."""
        if not prompt:
            return {"status": "success", "is_safe": True, "score": 0.0}
            
        lower_prompt = prompt.lower()
        
        # OMNI Security heuristic mock
        dangerous_keywords = ["ignore previous instructions", "system prompt", "you are now"]
        
        score = 0.0
        for kw in dangerous_keywords:
            if kw in lower_prompt:
                score += 0.4
                
        is_safe = score < self.sensitivity
        
        return {
            "status": "success",
            "is_safe": is_safe,
            "threat_score": min(1.0, score),
            "flagged_keywords": [kw for kw in dangerous_keywords if kw in lower_prompt]
        }
