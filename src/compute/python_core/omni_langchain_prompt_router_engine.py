from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err
import re

class OmniLangChainPromptRouterEngine:
    """
    omni-langchain-prompt-router
    
    A native topological constraints parser natively resolving parameter extraction 
    from template structural bounds mathematically, mapping behavior limits of LangChain 
    architectures completely dependency-free.
    """
    
    ENGINE_VERSION = "omni-s11-b5.1.0"
    
    def __init__(self) -> None:
        self.chain_metrics = 0

    def parse_and_route_parametric_template(self, raw_prompt_template: str, expected_inbound_keys: List[str]) -> Result:
        """
        Natively isolates string components to check valid structural bounds required 
        by architectural agent loops.
        """
        try:
            if not isinstance(raw_prompt_template, str) or not expected_inbound_keys:
                return Err(ValueError("Template sequence bounded matrix missing or malformed."))
                
            # Regex extracting `{key}` natively
            extracted_variables = re.findall(r'\{([a-zA-Z0-9_]+)\}', raw_prompt_template)
            
            missing_variables = []
            unexpected_variables = []
            
            extracted_set = set(extracted_variables)
            expected_set = set(expected_inbound_keys)
            
            for key in expected_set:
                if key not in extracted_set:
                    missing_variables.append(key)
                    
            for key in extracted_set:
                if key not in expected_set:
                    unexpected_variables.append(key)
                    
            is_perfect_match = (len(missing_variables) == 0 and len(unexpected_variables) == 0)
            
            if not is_perfect_match:
                return Err(ValueError(f"Prompt Schema Collision! Missing: {missing_variables}. Unexpected: {unexpected_variables}"))
                
            self.chain_metrics += len(expected_inbound_keys)
            
            return Ok({
                "template_validation_status": "perfect",
                "extracted_parameters_count": len(extracted_variables),
                "extracted_nodes": list(extracted_set)
            })
            
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides native bounds registry validations."""
        return {
            "engine": "OmniLangChainPromptRouterEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "linked_metrics_analyzed": self.chain_metrics,
            "complexity": "O(N) Token RegEx Limits"
        }
