# OMNI Compute Layer - FastChat Conversation Template
class FastChatError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def format_prompt_template(messages: list, system_prompt: str) -> Result:
    """Formats raw chat messages into a specific LLM chat template (e.g., Vicuna/Llama2)."""
    try:
        if not messages:
            return Result(error=FastChatError("Empty message list"))
            
        # Simulating Vicuna-style template formatting
        formatted = f"{system_prompt}\n"
        for msg in messages:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            formatted += f"{role}: {msg['content']}\n"
            
        return Result(value={"formatted_prompt": formatted})
    except Exception as e:
        return Result(error=FastChatError(f"Formatting failed: {str(e)}"))
