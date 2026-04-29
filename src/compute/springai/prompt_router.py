from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class PromptRouter:
    def route_query(self, query: str) -> OmniResult:
        if not query:
            return OmniResult(None, "Empty query")
            
        try:
            # Simple routing logic
            target = "rag_search" if "?" in query else "command_execution"
            return OmniResult(target)
        except Exception as e:
            return OmniResult(None, str(e))
