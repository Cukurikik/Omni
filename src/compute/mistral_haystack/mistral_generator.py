from typing import List, Dict

class MistralHaystackGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def run(self, prompt: str) -> Dict[str, List[str]]:
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        # Direct integration with Mistral models
        return {"replies": [f"Mistral Output: {prompt}"]}
