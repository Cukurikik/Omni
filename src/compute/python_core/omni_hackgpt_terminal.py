from typing import Dict, Any

class OmniHackGPTTerminal:
    """OMNI Compute Layer: HackGPT Interface Customization Engine"""
    
    def __init__(self, theme: str = "matrix"):
        self.theme = theme

    def format_output(self, raw_llm_response: str) -> str:
        if not raw_llm_response:
            return ""
            
        if self.theme == "matrix":
            return f"\033[92m{raw_llm_response}\033[0m" # Green terminal output
        elif self.theme == "hacker":
            return f"> root@hackgpt:~$ {raw_llm_response}"
        return raw_llm_response
