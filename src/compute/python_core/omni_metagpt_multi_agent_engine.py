"""OmniMetaGPTMultiAgentEngine.

Implements Standard Operating Procedure (SOP) role routing limits
for the MetaGPT multi-agent software company architecture.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniMetaGPTMultiAgentEngine:
    """Zero-mock engine for MetaGPT SOP role routing limits."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniMetaGPTMultiAgentEngine",
            "version": "1.0.0",
            "primitive": "sop_role_router",
            "monadic_enforcement": True,
        }

    @staticmethod
    def validate_sop_pipeline(roles: List[str]) -> Result:
        """
        MetaGPT requires a strict linear or DAG progression of roles
        (e.g., Product Manager -> Architect -> Engineer -> QA).
        """
        if not roles:
            return Err(ValueError("Role list is empty"))
            
        # Simplified MetaGPT standard progression
        standard_flow = ["PM", "ARCHITECT", "ENGINEER", "QA"]
        
        # Check if roles follow a logical progression
        isValid = True
        violations = []
        
        # Map indices
        indices = []
        for r in roles:
            r_upper = r.upper()
            if r_upper in standard_flow:
                indices.append(standard_flow.index(r_upper))
            else:
                violations.append(f"Unknown role: {r}")
                
        # Check for backwards progression
        for i in range(1, len(indices)):
            if indices[i] < indices[i-1]:
                isValid = False
                violations.append(f"Backward progression: {roles[i-1]} to {roles[i]}")
                
        return Ok({
            "is_valid_pipeline": isValid and len(violations) == 0,
            "roles": roles,
            "violations": violations
        })
