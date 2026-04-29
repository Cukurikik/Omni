# OMNI Compute Layer - AutoChat Agent
import json

class AgentError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def build_chat_context(history: list, new_message: str) -> Result:
    try:
        if not new_message.strip():
            return Result(error=AgentError("Cannot process empty message"))
            
        context = history.copy()
        context.append({"role": "user", "content": new_message})
        
        # Enforce token limits strictly
        token_estimate = sum(len(msg["content"].split()) for msg in context)
        if token_estimate > 4000:
            return Result(error=AgentError("Context window exceeded"))
            
        return Result(value=json.dumps(context))
    except Exception as e:
        return Result(error=AgentError(f"Agent processing failed: {str(e)}"))
