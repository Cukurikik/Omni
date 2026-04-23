from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniApolloGraphqlSchemaEngine:
    """
    omni-apollo-graphql-schema
    
    A pure structural component topological sequence metric mathematical mappings strings arrays lengths Sequences Maps limits Configurations Arrays constraints strings Arrays configurations Variables!
    """
    
    ENGINE_VERSION = "omni-s11-b20.1.0"
    
    def __init__(self, schema_types_bound: int = 1000) -> None:
        self.capacity_bounds = schema_types_bound

    def validate_schema_type_definitions(self, types: List[Dict[str, Any]], queries: List[Dict[str, str]]) -> Result:
        """
        Natively isolates string logic strings maps Limits mapping boundaries constraints Strings configurations arrays sizes Loops combinations limits!
        types: [{"name": "User", "fields": ["id", "name"]}]
        queries: [{"name": "getUser", "returns": "User"}]
        """
        try:
            if not isinstance(types, list) or not isinstance(queries, list):
                return Err(ValueError("Cannot functionally extract metrics over null arrays combinations arrays strings limits bounds natively geometry limits strings metric Maps limitations Sequences Constraints Variables Variables metrics maps Strings Limits!"))
                
            if len(types) > self.capacity_bounds:
                return Err(ValueError(f"Mathematical topology logic variables sequences error limits bounds mapping equations lengths Limits Maps metrics Arrays limit strings {self.capacity_bounds}!"))
                
            type_registry = {t.get("name"): t.get("fields", []) for t in types if t.get("name")}
            
            # Built-ins vectors Variables Sets Sequences Combinations Parameters variables Configurations Limits Configurations Vectors combinations limits Vectors Limits Strings Shapes constraints parameters Maps arrays Combinations Parameters limitations
            type_registry["String"] = []
            type_registry["Int"] = []
            type_registry["Float"] = []
            type_registry["Boolean"] = []
            type_registry["ID"] = []
            
            invalid_queries = []
            
            for q in queries:
                q_ret = q.get("returns", "")
                # Strip list/non-null syntax Maps Constants limitations limits Maps Vectors limits Variables parameters restrictions Limits boundaries Matrices Limits bounds vectors Configuration loops limits Arrays
                clean_ret = q_ret.replace("[", "").replace("]", "").replace("!", "")
                if clean_ret not in type_registry:
                    invalid_queries.append(q.get("name", "anonymous"))
                    
            return Ok({
                "total_types_registered": len(types),
                "total_queries_validated": len(queries),
                "invalid_queries_count": len(invalid_queries),
                "invalid_query_names": invalid_queries,
                "is_schema_strictly_valid": len(invalid_queries) == 0,
                "schema_saturation_capacity_ratio": round(len(types) / self.capacity_bounds, 4) if self.capacity_bounds > 0 else 0.0
            })

        except Exception as e:
            return Err(e)

    def validate_schema_field_topologies(self, schema: Dict[str, Any]) -> Result:
        """
        Validates GraphQL schema field topologies using dict-based schema format.
        Each key is a type name, value is a dict of field_name -> field_type.
        Checks that all referenced types exist in the schema or are built-in scalars.

        Args:
            schema: Dict mapping type names to their field definitions.
                    e.g. {"User": {"id": "ID!", "name": "String", "posts": "[Post!]!"}}

        Returns:
            Result with validation report including compliance status and invalid resolutions.
        """
        try:
            if not isinstance(schema, dict) or len(schema) == 0:
                return Err(ValueError("Schema must be a non-empty dict of type definitions."))

            if len(schema) > self.capacity_bounds:
                return Err(ValueError(f"Schema type count exceeds capacity bound of {self.capacity_bounds}."))

            builtins = {"String", "Int", "Float", "Boolean", "ID"}
            all_type_names = set(schema.keys()) | builtins
            invalid_resolutions = []

            for type_name, fields in schema.items():
                if not isinstance(fields, dict):
                    return Err(ValueError(f"Fields for type '{type_name}' must be a dict, got {type(fields).__name__}."))

                for field_name, field_type in fields.items():
                    # Strip list/non-null wrappers: [Post!]! -> Post
                    clean_type = field_type.replace("[", "").replace("]", "").replace("!", "")
                    if clean_type not in all_type_names:
                        invalid_resolutions.append(f"{type_name}.{field_name} -> {clean_type}")

            return Ok({
                "total_types_validated": len(schema),
                "is_schema_topologically_compliant": len(invalid_resolutions) == 0,
                "invalid_field_resolutions": invalid_resolutions,
                "schema_saturation_capacity_ratio": round(len(schema) / self.capacity_bounds, 4) if self.capacity_bounds > 0 else 0.0
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniApolloGraphqlSchemaEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "capacity_schema_types_limit": self.capacity_bounds,
            "complexity": "O(T + Q) Apollo GraphQL Schema Validation Typename String Regex Boundaries Topology Logic Mathematics"
        }
