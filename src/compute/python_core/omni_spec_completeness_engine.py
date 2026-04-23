"""OmniSpecCompletenessEngine for declarative manifest checking."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniSpecCompletenessEngine(OmniBaseEngine):
    """Production-grade Omni Spec Completeness Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def check_spec(self, spec: Dict[str, Any], required_fields: List[str], type_map: Dict[str, str] = None) -> Result[Dict[str, Any], str]:
        """
        Checks a dictionary specification against required fields and strict types.
        type_map takes string reprs like 'int', 'str', 'float', 'list', 'dict', 'bool'.
        """
        try:
            if not isinstance(spec, dict) or not isinstance(required_fields, list):
                return Result.fail("Invalid input shapes")

            missing_fields = []
            type_mismatches = {}

            python_type_map = {
                'int': int,
                'str': str,
                'float': float,
                'list': list,
                'dict': dict,
                'bool': bool
            }

            for field in required_fields:
                if field not in spec:
                    missing_fields.append(field)
                else:
                    if type_map and field in type_map:
                        expected_type_str = type_map[field]
                        if expected_type_str in python_type_map:
                            expected_type = python_type_map[expected_type_str]
                            if not isinstance(spec[field], expected_type):
                                type_mismatches[field] = {
                                    "expected": expected_type_str,
                                    "actual": type(spec[field]).__name__
                                }

            is_complete = len(missing_fields) == 0 and len(type_mismatches) == 0

            return Result.ok({
                "is_complete": is_complete,
                "missing_fields": missing_fields,
                "type_mismatches": type_mismatches
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniSpecCompletenessEngine",
            "status": "operational",
            "complexity": "O(N)"
        }
