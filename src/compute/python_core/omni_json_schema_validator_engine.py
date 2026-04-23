"""OmniJsonSchemaValidatorEngine — Production-grade JSON schema validation.

Implements a subset of JSON Schema (Draft 7) validation including type checking,
required fields, min/max constraints, pattern matching, enum validation,
and nested object/array validation — all in pure Python.
"""
import re
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniJsonSchemaValidatorEngine:
    """Production engine for JSON schema validation."""

    ENGINE_VERSION = "1.0.0"

    TYPE_MAP = {
        "string": str, "number": (int, float), "integer": int,
        "boolean": bool, "array": list, "object": dict, "null": type(None)
    }

    def validate(self, data: Any, schema: Dict[str, Any]) -> Result:
        """
        Validate data against a JSON schema.

        Args:
            data: The data to validate.
            schema: JSON Schema definition (subset of Draft 7).

        Returns:
            Result with validation status and list of errors.
        """
        try:
            errors = []
            self._validate_node(data, schema, "", errors)
            return Ok({"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)})
        except Exception as e:
            return Err(e)

    def _validate_node(self, data: Any, schema: Dict[str, Any], path: str, errors: List[Dict]):
        # Type check
        if "type" in schema:
            expected = schema["type"]
            expected_types = self.TYPE_MAP.get(expected)
            if expected_types and not isinstance(data, expected_types):
                # bool is subclass of int, filter it
                if expected == "integer" and isinstance(data, bool):
                    errors.append({"path": path, "error": f"Expected {expected}, got {type(data).__name__}"})
                    return
                elif expected != "boolean" or not isinstance(data, bool):
                    if not (expected == "number" and isinstance(data, bool)):
                        pass
                    else:
                        errors.append({"path": path, "error": f"Expected {expected}, got bool"})
                        return
                if not isinstance(data, expected_types) or (expected == "integer" and isinstance(data, bool)):
                    errors.append({"path": path, "error": f"Expected {expected}, got {type(data).__name__}"})
                    return

        # Enum
        if "enum" in schema:
            if data not in schema["enum"]:
                errors.append({"path": path, "error": f"Value must be one of {schema['enum']}"})

        # String constraints
        if isinstance(data, str):
            if "minLength" in schema and len(data) < schema["minLength"]:
                errors.append({"path": path, "error": f"String too short (min {schema['minLength']})"})
            if "maxLength" in schema and len(data) > schema["maxLength"]:
                errors.append({"path": path, "error": f"String too long (max {schema['maxLength']})"})
            if "pattern" in schema and not re.search(schema["pattern"], data):
                errors.append({"path": path, "error": f"String does not match pattern '{schema['pattern']}'"})

        # Number constraints
        if isinstance(data, (int, float)) and not isinstance(data, bool):
            if "minimum" in schema and data < schema["minimum"]:
                errors.append({"path": path, "error": f"Value {data} < minimum {schema['minimum']}"})
            if "maximum" in schema and data > schema["maximum"]:
                errors.append({"path": path, "error": f"Value {data} > maximum {schema['maximum']}"})

        # Object constraints
        if isinstance(data, dict):
            if "required" in schema:
                for field in schema["required"]:
                    if field not in data:
                        errors.append({"path": f"{path}.{field}", "error": f"Required field missing"})
            if "properties" in schema:
                for prop, prop_schema in schema["properties"].items():
                    if prop in data:
                        self._validate_node(data[prop], prop_schema, f"{path}.{prop}", errors)

        # Array constraints
        if isinstance(data, list):
            if "minItems" in schema and len(data) < schema["minItems"]:
                errors.append({"path": path, "error": f"Array too short (min {schema['minItems']})"})
            if "maxItems" in schema and len(data) > schema["maxItems"]:
                errors.append({"path": path, "error": f"Array too long (max {schema['maxItems']})"})
            if "items" in schema:
                for i, item in enumerate(data):
                    self._validate_node(item, schema["items"], f"{path}[{i}]", errors)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniJsonSchemaValidatorEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "supported": "type, required, min/max, pattern, enum, nested"}
