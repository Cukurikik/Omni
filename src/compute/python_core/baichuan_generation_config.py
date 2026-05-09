from typing import Dict, Any

class BaichuanGenerationConfig:
    def __init__(self, top_p: float = 0.9, top_k: int = 50):
        self.top_p = top_p
        self.top_k = top_k

    def get_config(self) -> Dict[str, Any]:
        return {"top_p": self.top_p, "top_k": self.top_k}
