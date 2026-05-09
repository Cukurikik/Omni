"""OMNI Compute — Structured Output / JSON Schema Enforcer"""
import json, re, logging; from typing import Dict, List, Any, Optional
logger = logging.getLogger("omni.structured")

class StructuredOutputEnforcer:
    """Force LLM output to conform to JSON schema."""
    def __init__(self):
        self.schemas: Dict[str, Dict] = {}
    def register_schema(self, name: str, schema: Dict):
        self.schemas[name] = schema
    def validate(self, output: str, schema_name: str) -> Dict[str, Any]:
        schema = self.schemas.get(schema_name)
        if not schema: raise ValueError(f"Schema {schema_name} not found")
        # Extract JSON from output
        json_str = self._extract_json(output)
        parsed = json.loads(json_str)
        errors = self._validate_against_schema(parsed, schema)
        return {"valid": len(errors) == 0, "data": parsed, "errors": errors}
    def _extract_json(self, text: str) -> str:
        patterns = [r'```json\s*([\s\S]*?)\s*```', r'```\s*([\s\S]*?)\s*```', r'(\{[\s\S]*\})', r'(\[[\s\S]*\])']
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                try: json.loads(match.group(1)); return match.group(1)
                except: continue
        return text
    def _validate_against_schema(self, data: Any, schema: Dict) -> List[str]:
        errors = []
        if "type" in schema:
            expected = schema["type"]
            type_map = {"string": str, "number": (int, float), "integer": int, "boolean": bool, "array": list, "object": dict}
            if expected in type_map and not isinstance(data, type_map[expected]):
                errors.append(f"Expected {expected}, got {type(data).__name__}")
                return errors
        if "required" in schema and isinstance(data, dict):
            for field in schema["required"]:
                if field not in data: errors.append(f"Missing required field: {field}")
        if "properties" in schema and isinstance(data, dict):
            for key, prop_schema in schema["properties"].items():
                if key in data:
                    sub_errors = self._validate_against_schema(data[key], prop_schema)
                    errors.extend([f"{key}.{e}" for e in sub_errors])
        if "items" in schema and isinstance(data, list):
            for i, item in enumerate(data):
                sub_errors = self._validate_against_schema(item, schema["items"])
                errors.extend([f"[{i}].{e}" for e in sub_errors])
        if "enum" in schema and data not in schema["enum"]:
            errors.append(f"Value {data} not in enum {schema['enum']}")
        return errors
    def create_prompt_suffix(self, schema_name: str) -> str:
        schema = self.schemas.get(schema_name, {})
        return f"\n\nRespond ONLY with valid JSON matching this schema:\n```json\n{json.dumps(schema, indent=2)}\n```"
