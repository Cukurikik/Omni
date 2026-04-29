from typing import Dict, List

class OmniChatLLAMABot:
    """OMNI Compute Layer: Chat-LLaMA Discord Bot Engine"""
    
    def __init__(self, prefix: str = "!"):
        self.prefix = prefix
        self.command_registry = ["chat", "reset", "help"]

    def parse_message(self, message: str) -> Dict[str, str]:
        if not message.startswith(self.prefix):
            return {"type": "text", "payload": message}
            
        parts = message[len(self.prefix):].split(" ", 1)
        command = parts[0]
        payload = parts[1] if len(parts) > 1 else ""
        
        if command in self.command_registry:
            return {"type": "command", "command": command, "payload": payload}
        return {"type": "unknown"}
