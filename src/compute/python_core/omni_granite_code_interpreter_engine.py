"""OmniGraniteCodeInterpreterEngine.

Provides static security analysis and execution sandbox bounds checking
for code interpreted by IBM Granite-style code models.
"""
import sys
import os
import ast
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniGraniteCodeInterpreterEngine:
    """Zero-mock engine for analyzing executable code boundaries."""

    DANGEROUS_IMPORTS = {"os", "sys", "subprocess", "pty", "shlex", "socket"}
    DANGEROUS_CALLS = {"eval", "exec", "open", "compile", "__import__"}

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniGraniteCodeInterpreterEngine",
            "version": "1.0.0",
            "primitive": "code_security_sandbox",
            "monadic_enforcement": True,
        }

    @staticmethod
    def analyze_sandbox_safety(code_string: str) -> Result:
        """
        Statically checks code for dangerous imports and builtin calls.
        """
        if not code_string.strip():
            return Err(ValueError("Code string is empty"))
            
        try:
            tree = ast.parse(code_string)
        except SyntaxError as e:
            return Err(ValueError(f"Syntax Error: {e}"))
            
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in OmniGraniteCodeInterpreterEngine.DANGEROUS_IMPORTS:
                        violations.append(f"Dangerous import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in OmniGraniteCodeInterpreterEngine.DANGEROUS_IMPORTS:
                        violations.append(f"Dangerous from import: {node.module}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in OmniGraniteCodeInterpreterEngine.DANGEROUS_CALLS:
                        violations.append(f"Dangerous call: {node.func.id}")
                        
        if violations:
            return Ok({
                "safe": False,
                "violations": violations
            })
            
        return Ok({
            "safe": True,
            "violations": []
        })
