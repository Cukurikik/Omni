from typing import Dict, Any, Type
from dataclasses import dataclass
import json

try:
    from pydantic import BaseModel, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    class BaseModel: pass

# OMNI Genai Pydantic Processor Engine — Compute Layer
# Absorbing mbeacom/genai-processors-pydantic
# Structured schema injection and runtime validation for LLM generative outputs.

@dataclass
class GenaiPydanticResult:
    ok: bool
    parsed_object: Any = None
    validation_error: str = None

class OmniGenaiPydanticProcessor:
    def __init__(self):
        self.processings = 0

    def parse_and_validate(self, raw_llm_json: str, schema_class: Type[BaseModel]) -> GenaiPydanticResult:
        """
        Takes raw string output from an LLM and validates it against a Pydantic schema model.
        Returns the instantiated model or detailed validation constraints.
        """
        if not PYDANTIC_AVAILABLE:
            return GenaiPydanticResult(False, validation_error="PydanticProcessorError: library unavailable")
            
        try:
            self.processings += 1
            
            # Clean possible markdown formatting
            cleaned = raw_llm_json.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
                
            data_dict = json.loads(cleaned.strip())
            
            # Validate
            validated_obj = schema_class(**data_dict)
            return GenaiPydanticResult(True, parsed_object=validated_obj)
            
        except json.JSONDecodeError as e:
            return GenaiPydanticResult(False, validation_error=f"JSON Decode Error: {str(e)}")
        except Exception as e:
            # Reaches here if validation fails gracefully
            return GenaiPydanticResult(False, validation_error=f"Validation error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniGenaiPydanticProcessor", "processings": self.processings,
                "status": "Operational" if PYDANTIC_AVAILABLE else "Disabled"}
