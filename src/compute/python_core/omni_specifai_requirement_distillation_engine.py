"""
OmniSpecifaiRequirementDistillationEngine (Level-2 Abstraction)
Assimilated from: presidio-oss/specif-ai
Domain: BRD/PRD Semantic Logic Constraint Validation
"""

from typing import Dict, Any, List, Optional

from dataclasses import dataclass
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniSpecifaiRequirementDistillationEngine:
    """
    Distills raw structural requirements into non-contradictory logic constraints.
    Validates cyclic dependencies and exclusionary rules within business requirement layers.
    """
    
    @staticmethod
    def distill_logic_constraints(requirements: List[Dict[str, Any]]) -> Result:
        """Perform distill logic constraints computation.

            Args:
                    requirements: List[Dict[str
                    Any]]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not requirements:
            return Err("FATAL: Requirements payload cannot be empty.")
            
        constraint_graph = {}
        for idx, req in enumerate(requirements):
            req_id = req.get("id")
            if not req_id:
                return Err(f"CRITICAL: Requirement at index {idx} lacks an identity token.")
                
            deps = req.get("dependencies", [])
            mutex = req.get("mutually_exclusive", [])
            
            # Mutual exclusion check
            for m in mutex:
                if m in deps:
                    return Err(f"CONTRADICTION: Requirement {req_id} depends on and is mutually exclusive with {m}.")
                    
            constraint_graph[req_id] = {"deps": deps, "mutex": mutex}
            
        # Detect cyclic dependencies natively without external libs
        visited = set()
        rec_stack = set()
        
        def is_cyclic(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in constraint_graph.get(node, {}).get("deps", []):
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False
            
        for node in constraint_graph:
            if node not in visited:
                if is_cyclic(node):
                    return Err("TOPOLOGY ERROR: Cyclic dependency detected in requirement graph.")
                    
        return Ok({
            "total_nodes": len(constraint_graph),
            "graph_integrity": "VALIDATED",
            "cyclic": False
        })

    @staticmethod
    def diagnostics() -> Dict[str, Any]:
        return {
            "engine": "OmniSpecifaiRequirementDistillationEngine",
            "status": "operational",
            "monadic_enforcement": True
        }
