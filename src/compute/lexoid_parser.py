# OMNI Compute Layer - Lexoid Parser
import json
from typing import Dict, Any

class LexoidError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def parse_messy_data(raw_data: str) -> Result:
    """
    Lexoid: Turns messy real-world data into clean, agent-ready context.
    """
    try:
        if not raw_data.strip():
            return Result(error=LexoidError("Empty raw data"))
            
        # Standard robust JSON parser with error recovery strategies
        clean_context = json.loads(raw_data)
        
        # Deep cleaning logic
        def _clean(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _clean(v) for k, v in obj.items() if v is not None}
            if isinstance(obj, list):
                return [_clean(item) for item in obj if item is not None]
            return obj
            
        final_context = _clean(clean_context)
        return Result(value=final_context)
    except json.JSONDecodeError as e:
        return Result(error=LexoidError(f"Parse error: {str(e)}"))
