"""
OMNI Open Interpreter Agent Engine
Production structural verification of abstract syntax trees.
"""
import ast
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniOpenInterpreterAgentEngine(OmniBaseEngine):
    def __init__(self, allowed_imports: List[str] = None):
        super().__init__()
        self.allowed_imports = allowed_imports or ["math", "os", "sys", "json", "numpy"]

    def process(self, code_payload: str) -> Result[bool, str]:
        if not code_payload.strip():
            return Err("Code payload is empty.")
            
        try:
            tree = ast.parse(code_payload)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split('.')[0] not in self.allowed_imports:
                            return Err(f"Unauthorized import violation: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.split('.')[0] not in self.allowed_imports:
                        return Err(f"Unauthorized import violation: {node.module}")
            return Ok(True)
        except SyntaxError as e:
            return Err(f"Syntax validation failed: {str(e)}")
        except Exception as e:
            return Err(f"AST parsing fatal error: {str(e)}")

    def diagnostics(self) -> Result[Dict[str, Any], str]:
        test_code = "import math\nx = math.sqrt(4)"
        res = self.process(test_code)
        if hasattr(res, 'is_ok') and res.is_ok():
            return Ok({"status": "healthy", "allowed_imports": self.allowed_imports})
        return Err("Diagnostics failed on Open Interpreter engine.")
