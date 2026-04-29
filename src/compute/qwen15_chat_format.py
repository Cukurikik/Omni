# OMNI Compute Layer - Qwen1.5 Chat Format
class QwenError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def format_qwen15_prompt(messages: list) -> Result:
    """Formats a message history into Qwen1.5 ChatML template."""
    try:
        if not messages:
            return Result(error=QwenError("Messages list is empty"))
            
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
            
        prompt += "<|im_start|>assistant\n"
        
        return Result(value={"formatted_prompt": prompt})
    except Exception as e:
        return Result(error=QwenError(f"Formatting failed: {str(e)}"))
