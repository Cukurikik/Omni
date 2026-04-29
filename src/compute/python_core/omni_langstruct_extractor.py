from typing import Dict, Any
import json

class OmniLangstructExtractor:
    """OMNI Compute Layer: Langstruct Structured Data Extractor"""
    
    def __init__(self, strict_mode: bool = True):
        self.strict = strict_mode

    def extract_json(self, raw_llm_output: str) -> Dict[str, Any]:
        if not raw_llm_output:
            return {}
            
        try:
            # Deterministic attempt to find JSON block
            start_idx = raw_llm_output.find("{")
            end_idx = raw_llm_output.rfind("}")
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = raw_llm_output[start_idx:end_idx+1]
                return json.loads(json_str)
            else:
                if self.strict:
                    raise ValueError("No JSON block found")
                return {"raw_text": raw_llm_output}
        except Exception as e:
            return {"error": str(e)}
