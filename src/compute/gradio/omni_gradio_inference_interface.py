# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Gradio Inference Interface (OMNI Zero-Mock Implementation)
# Implements RESTful pipeline input validation without magic parameters.

from dataclasses import dataclass
from typing import Dict, Any, Optional
import json

@dataclass
class Result:
    value: Optional[Dict[str, Any]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: Dict[str, Any]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class GradioRestRouter:
    def __init__(self, required_types: Dict[str, str]):
        self.required_types = required_types

    def safe_parse_payload(self, raw_json_payload: str) -> Result:
        try:
            parsed = json.loads(raw_json_payload)
        except Exception:
            return Result.err("Invalid JSON encoding.")

        for key, expected_type in self.required_types.items():
            if key not in parsed:
                return Result.err(f"Missing required key: {key}")
                
            val = parsed[key]
            if expected_type == "float" and not isinstance(val, (float, int)):
                return Result.err(f"Field {key} must be a float.")
            if expected_type == "string" and not isinstance(val, str):
                return Result.err(f"Field {key} must be a string.")
            if expected_type == "list" and not isinstance(val, list):
                return Result.err(f"Field {key} must be a list.")

        return Result.ok(parsed)
