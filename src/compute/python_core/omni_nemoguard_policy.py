from typing import Dict, Any

class OmniNeMoGuardPolicy:
    """OMNI Compute Layer: NeMo-Guardrails Policy Enforcement"""
    
    def __init__(self, block_prompt_injection: bool = True):
        self.block_prompt_injection = block_prompt_injection

    def check_rails(self, user_input: str) -> Dict[str, Any]:
        if not user_input:
            return {"allowed": True, "reason": "empty"}
            
        lower_input = user_input.lower()
        if self.block_prompt_injection and ("ignore previous instructions" in lower_input or "system prompt" in lower_input):
            return {"allowed": False, "reason": "Prompt Injection Detected"}
            
        return {"allowed": True, "reason": "Clear"}
