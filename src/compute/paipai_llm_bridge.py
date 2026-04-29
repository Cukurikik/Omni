# OMNI Compute Layer - PaiPai LLM Bridge
class PaiError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def process_im_message_for_ai(message: dict) -> Result:
    """Bridges Instant Messaging content with AI language models."""
    try:
        if "text" not in message or "sender_id" not in message:
            return Result(error=PaiError("Invalid IM message format"))
            
        ai_directive = f"User {message['sender_id']} says: {message['text']}. Respond concisely."
        
        return Result(value={"processed_directive": ai_directive, "is_cmd": message['text'].startswith("/")})
    except Exception as e:
        return Result(error=PaiError(f"Bridge processing failed: {str(e)}"))
