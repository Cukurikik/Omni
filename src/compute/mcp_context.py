# OMNI Compute Layer - MCP Context Parser
import json

class MCPContextError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def parse_mcp_context(raw_json: str) -> Result:
    """Parses context for the Model Context Protocol."""
    try:
        data = json.loads(raw_json)
        if "context_window" not in data:
            return Result(error=MCPContextError("Missing context_window"))
            
        return Result(value=data["context_window"])
    except json.JSONDecodeError as e:
        return Result(error=MCPContextError(f"Invalid JSON: {str(e)}"))
    except Exception as e:
        return Result(error=MCPContextError(f"Parse error: {str(e)}"))
