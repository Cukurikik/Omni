from __future__ import annotations
from typing import Dict, Any, List
import re
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniGraphQLSchemaResolverEngine:
    """
    omni-graphql-schema-resolver
    
    A native structural bounding string abstraction engine mathematically querying JSON 
    nested mappings imitating a resolved execution of a GraphQL AST without actual parser bounds!
    """
    
    ENGINE_VERSION = "omni-s11-b5.1.0"
    
    def __init__(self) -> None:
        pass

    def extract_nested_payload(self, raw_graphql_query: str, root_data_matrix: Dict[str, Any]) -> Result:
        """
        Natively isolates string components checking valid structural bounds required 
        by returning JSON mapped objects directly.
        Does a flat match parsing: '{ user { id name } }' -> resolving those structurally.
        """
        try:
            if not raw_graphql_query or not root_data_matrix:
                return Err(ValueError("Cannot structural compute GraphQL metrics without bounds mappings!"))
                
            # A deeply mathematical but very constrained basic parser
            # We strip spaces and formatting.
            clean_query = raw_graphql_query.replace("\n", " ").strip()
            
            # Use regex to find fields in bounded blocks { ... }
            # For this MVP limit, we handle one depth level: { entity { field1 field2 } }
            mat = re.search(r'\{\s*(\w+)\s*\{\s*([^}]+)\s*\}\s*\}', clean_query)
            
            if not mat:
                return Err(ValueError("Structural bounds schema limit reached. Query must match: { entity { field... } }"))
                
            entity = mat.group(1).strip()
            fields_str = mat.group(2).strip()
            fields = fields_str.split()
            
            if not fields:
                return Err(ValueError("Missing projected structural field metrics!"))
                
            if entity not in root_data_matrix:
                return Ok({"errors": [{"message": f"Cannot query field '{entity}' on root type."}], "data": None})
                
            entity_data = root_data_matrix[entity]
            resolved_dict = {}
            
            # Handle List array constraints
            if isinstance(entity_data, list):
                resolved_list = []
                for item in entity_data:
                    local_obj = {}
                    for f in fields:
                        if f in item:
                            local_obj[f] = item[f]
                    resolved_list.append(local_obj)
                resolved_dict = resolved_list
            elif isinstance(entity_data, dict):
                for f in fields:
                    if f in entity_data:
                        resolved_dict[f] = entity_data[f]
            else:
                return Err(ValueError(f"Topological root entity '{entity}' resolves to unstructured scaler primitive!"))
                
            return Ok({
                "data": {
                    entity: resolved_dict
                }
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides native GraphQL registry verifications."""
        return {
            "engine": "OmniGraphQLSchemaResolverEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "complexity": "O(N) Regex Topological Bounding Graph Match"
        }
