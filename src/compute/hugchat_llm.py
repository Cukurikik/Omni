# OMNI Compute Layer - HugChat LLM
class HugChatError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def format_hugchat_prompt(system_prompt: str, user_input: str) -> Result:
    """Formats prompt for HugChat inference."""
    try:
        if not user_input.strip():
            return Result(error=HugChatError("Empty user input"))
            
        formatted = f"<|system|>\n{system_prompt}</s>\n<|user|>\n{user_input}</s>\n<|assistant|>\n"
        return Result(value=formatted)
    except Exception as e:
        return Result(error=HugChatError(f"Format error: {str(e)}"))
