"""
OmniPyrusticMetastatePolicyEngine (Level-2 Abstraction)
Assimilated from: pyrustic/pyrustic
Domain: Architectural Policy Enforcement
"""

from typing import Dict, Any, List, Optional

from dataclasses import dataclass
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniPyrusticMetastatePolicyEngine:
    """
    Enforces decoupling policies across application metastates. 
    Prevents layer violations across strictly segregated execution domains.
    """
    
    @staticmethod
    def enforce_policy_matrix(components: List[Dict[str, str]], allowed_transitions: Dict[str, List[str]]) -> Result:
        """Perform enforce policy matrix computation.

            Args:
                    components: List[Dict[str
                    str]]
                    allowed_transitions: Dict[str
                    List[str]]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not components:
            return Err("FATAL: Component topology is empty.")
            
        if not allowed_transitions:
            return Err("FATAL: Allowed transitions matrix is empty.")
            
        registered_layers = set(allowed_transitions.keys())
        
        # Validate node layer registration
        for comp in components:
            c_name = comp.get("name")
            c_layer = comp.get("layer")
            if not c_name or not c_layer:
                return Err("CRITICAL: Component missing name or layer definition.")
            if c_layer not in registered_layers:
                return Err(f"VIOLATION: Component {c_name} resides in unregistered layer: {c_layer}")
                
            calls = comp.get("calls_to", "").split(",") if comp.get("calls_to") else []
            for target in calls:
                target = target.strip()
                if not target:
                    continue
                    
                target_comp = next((c for c in components if c.get("name") == target), None)
                if not target_comp:
                    return Err(f"VIOLATION: Component {c_name} calls undefined target {target}.")
                    
                target_layer = target_comp.get("layer")
                if target_layer not in allowed_transitions.get(c_layer, []):
                    return Err(f"ARCHITECTURAL VIOLATION: {c_layer} cannot transition to {target_layer} ({c_name} -> {target}).")
                    
        return Ok({
            "components_validated": len(components),
            "policy_status": "ENFORCED",
            "violations": 0
        })

    @staticmethod
    def diagnostics() -> Dict[str, Any]:
        return {
            "engine": "OmniPyrusticMetastatePolicyEngine",
            "status": "operational",
            "monadic_enforcement": True
        }
