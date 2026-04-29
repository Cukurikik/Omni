# OMNI Compute Layer - OpenCode Executor Sandbox
class SandboxError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def evaluate_code_safety(code_string: str) -> Result:
    """Statically analyzes python code for OpenCodeInterpreter sandbox."""
    try:
        if not code_string:
            return Result(error=SandboxError("Code string empty"))
            
        banned_imports = ["os", "sys", "subprocess", "pty"]
        for mod in banned_imports:
            if f"import {mod}" in code_string or f"from {mod}" in code_string:
                return Result(value={"safe": False, "reason": f"Banned module {mod}"})
                
        return Result(value={"safe": True, "reason": "No banned modules detected"})
    except Exception as e:
        return Result(error=SandboxError(f"Safety evaluation failed: {str(e)}"))
