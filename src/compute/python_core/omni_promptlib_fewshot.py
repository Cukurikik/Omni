from typing import List

class OmniPromptLibFewShot:
    """OMNI Compute Layer: Prompt-Lib Few-Shot Engine"""
    
    def __init__(self, separator: str = "\\n---\\n"):
        self.separator = separator

    def build_prompt(self, demonstrations: List[str], query: str) -> str:
        if not demonstrations:
            return query
            
        full_prompt = self.separator.join(demonstrations)
        full_prompt += self.separator + query
        
        return full_prompt
