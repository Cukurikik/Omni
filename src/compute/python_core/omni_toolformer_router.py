from typing import Dict, Any, Callable

class OmniToolformerRouter:
    """OMNI Compute Layer: Toolformer API Router (Zero-Mock)"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable) -> bool:
        if name in self.tools:
            return False
        self.tools[name] = func
        return True

    def execute_tool_call(self, call_string: str) -> str:
        # Expected format: "ToolName(arg)"
        if "(" not in call_string or not call_string.endswith(")"):
            return "Error: Invalid tool call format"
            
        parts = call_string.split("(", 1)
        name = parts[0]
        arg = parts[1][:-1]
        
        if name not in self.tools:
            return f"Error: Tool {name} not found"
            
        try:
            res = self.tools[name](arg)
            return str(res)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
