"""OmniFieldenmsTgEntityValidationEngine — Domain-Driven Entity Validation.

Inspired by fieldenms/tg (Trident Genesis): a Java-based DDD platform
for building enterprise applications with rich domain models, entity
companion objects, and property-level validation.

Algorithmic Primitive:
    Given a domain entity defined by a schema of typed properties with
    validation rules (required, min/max, regex, custom predicates),
    validate an entity instance against its schema. Compute a validation
    report with per-property pass/fail status and aggregate validity.
"""
from __future__ import annotations
import re
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniFieldenmsTgEntityValidationEngine:
    """Production-grade domain entity validator with schema-driven rules."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniFieldenmsTgEntityValidationEngine",
            "version": "1.0.0",
            "primitive": "schema_driven_entity_property_validation",
            "monadic_enforcement": True,
            "source_repo": "fieldenms/tg",
        }

    @staticmethod
    def validate_entity(schema: list[dict], entity: dict) -> Result:
        """Validate an entity against a property schema.

        Args:
            schema: List of property definitions, each with:
                - 'name': str — property name
                - 'type': str — expected type ('str', 'int', 'float', 'bool')
                - 'required': bool — whether the property must be present
                - 'min': optional numeric — minimum value (for int/float)
                - 'max': optional numeric — maximum value (for int/float)
                - 'pattern': optional str — regex pattern (for str type)
                - 'min_length': optional int — minimum string length
                - 'max_length': optional int — maximum string length
            entity: dict of property_name -> value.

        Returns:
            Result[dict, Exception]: dict with 'valid' (bool),
            'errors' (list of error strings), 'checked_count' (int).
        """
        if not isinstance(schema, list):
            return Err(Exception("schema must be a list of property definitions"))
        if not isinstance(entity, dict):
            return Err(Exception("entity must be a dict"))

        TYPE_MAP = {'str': str, 'int': int, 'float': (int, float), 'bool': bool}
        errors: list[str] = []

        for prop_def in schema:
            name = prop_def.get("name")
            if not name:
                return Err(Exception("Each property definition must have a 'name'"))

            required = prop_def.get("required", False)
            value = entity.get(name)

            # Required check
            if value is None:
                if required:
                    errors.append(f"Property '{name}' is required but missing")
                continue

            # Type check
            expected_type_str = prop_def.get("type")
            if expected_type_str and expected_type_str in TYPE_MAP:
                expected = TYPE_MAP[expected_type_str]
                if not isinstance(value, expected):
                    errors.append(
                        f"Property '{name}' expected type '{expected_type_str}', "
                        f"got '{type(value).__name__}'"
                    )
                    continue

            # Numeric range checks
            if isinstance(value, (int, float)):
                if "min" in prop_def and value < prop_def["min"]:
                    errors.append(
                        f"Property '{name}' value {value} below minimum {prop_def['min']}"
                    )
                if "max" in prop_def and value > prop_def["max"]:
                    errors.append(
                        f"Property '{name}' value {value} above maximum {prop_def['max']}"
                    )

            # String validation
            if isinstance(value, str):
                if "min_length" in prop_def and len(value) < prop_def["min_length"]:
                    errors.append(
                        f"Property '{name}' length {len(value)} below minimum {prop_def['min_length']}"
                    )
                if "max_length" in prop_def and len(value) > prop_def["max_length"]:
                    errors.append(
                        f"Property '{name}' length {len(value)} above maximum {prop_def['max_length']}"
                    )
                if "pattern" in prop_def:
                    if not re.match(prop_def["pattern"], value):
                        errors.append(
                            f"Property '{name}' does not match pattern '{prop_def['pattern']}'"
                        )

        return Ok({
            "valid": len(errors) == 0,
            "errors": errors,
            "checked_count": len(schema),
        })

    @staticmethod
    def validate_entity_relationships(
        entities: dict[str, dict],
        relationships: list[tuple[str, str]],
    ) -> Result:
        """Validate that all relationship references exist.

        Args:
            entities: dict of entity_id -> entity_data.
            relationships: list of (from_id, to_id) tuples.

        Returns:
            Result[dict, Exception]: dict with 'valid', 'broken_refs'.
        """
        if not isinstance(entities, dict):
            return Err(Exception("entities must be a dict"))
        if not isinstance(relationships, list):
            return Err(Exception("relationships must be a list of tuples"))

        broken: list[tuple[str, str]] = []
        for from_id, to_id in relationships:
            if from_id not in entities:
                broken.append((from_id, to_id))
            elif to_id not in entities:
                broken.append((from_id, to_id))

        return Ok({
            "valid": len(broken) == 0,
            "broken_refs": broken,
            "total_relationships": len(relationships),
        })
