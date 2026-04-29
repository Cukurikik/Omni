from typing import Any, Callable

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class TaskExecutor:
    def execute_remote(self, func: Callable, *args) -> OmniResult:
        if not func:
            return OmniResult(None, "Invalid function")
            
        try:
            # Python Ray distributed task execution logic
            result = func(*args)
            
            return OmniResult(result)
        except Exception as e:
            return OmniResult(None, str(e))
