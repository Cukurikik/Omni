from typing import Dict, Any

class OmniLLMJSAdapter:
    """OMNI Compute Layer: LLM.js Universal Adapter (Zero-Mock)"""
    
    def __init__(self, default_model: str):
        self.model = default_model

    def adapt_payload(self, raw_prompt: str, provider: str) -> Dict[str, Any]:
        if not raw_prompt:
            raise ValueError("Prompt cannot be empty")
            
        base_payload = {
            "model": self.model,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        if provider == "openai":
            base_payload["messages"] = [{"role": "user", "content": raw_prompt}]
        elif provider == "anthropic":
            base_payload["prompt"] = f"\n\nHuman: {raw_prompt}\n\nAssistant:"
        else:
            base_payload["prompt"] = raw_prompt
            
        return base_payload
