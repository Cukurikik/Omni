"""OmniDSCoderInstructEngine.

Analyzes adherence to DeepSeek Coder Instruct's rigorous format
for system prompts and instruction tuning structures.
"""
import sys
import os
import re
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniDSCoderInstructEngine:
    """Production zero-mock engine for DeepSeek instruction validation."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniDSCoderInstructEngine",
            "version": "1.0.0",
            "primitive": "instruct_format_validator",
            "monadic_enforcement": True,
        }

    @staticmethod
    def validate_instruct_format(prompt: str) -> Result:
        """
        DeepSeek Coder Instruct heavily relies on strict system and user
        delimiters. Ensures the prompt does not break boundaries.
        """
        if not prompt:
            return Err(ValueError("Prompt is empty"))
            
        # Typical DeepSeek Instruct template pattern
        sys_count = prompt.count("### System Prompt:")
        user_count = prompt.count("### User:")
        response_count = prompt.count("### Response:")
        
        is_valid = True
        violations = []
        
        if sys_count > 1:
            is_valid = False
            violations.append("Multiple System Prompts detected")
            
        if user_count != response_count:
            is_valid = False
            violations.append(f"Mismatched User ({user_count}) and Response ({response_count}) tags")
            
        return Ok({
            "is_format_valid": is_valid,
            "system_tags": sys_count,
            "user_tags": user_count,
            "response_tags": response_count,
            "violations": violations
        })
