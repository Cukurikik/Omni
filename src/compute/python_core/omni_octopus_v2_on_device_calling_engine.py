"""OmniOctopusV2OnDeviceCallingEngine.

Translates on-device edge AI functional tokens into 
direct API executions mapping for Octopus v2 architectures.
"""
import sys
import os
import re
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniOctopusV2OnDeviceCallingEngine:
    """Production engine for functional token extraction in edge models."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniOctopusV2OnDeviceCallingEngine",
            "version": "1.0.0",
            "primitive": "edge_functional_token_parser",
            "monadic_enforcement": True,
        }

    @staticmethod
    def extract_functional_tokens(output: str) -> Result:
        """
        Octopus v2 uses specialized functional tokens to reduce context size.
        """
        if not output:
            return Err(ValueError("Output string is empty"))
            
        call_pattern = re.compile(r"<n_call>\s*([a-zA-Z0-9_]+)")
        param_pattern = re.compile(r"<n_param>\s*([a-zA-Z0-9_]+)=([^<]+)")
        
        call_match = call_pattern.search(output)
        if not call_match:
            return Err(ValueError("No <n_call> token found"))
            
        function_name = call_match.group(1).strip()
        
        params = {}
        for param_match in param_pattern.finditer(output):
            key = param_match.group(1).strip()
            val = param_match.group(2).strip()
            params[key] = val
            
        return Ok({
            "function": function_name,
            "parameters": params,
            "token_efficiency": len(output)
        })
