import torch
from typing import Dict, Any

class HOIPostProcessor:
    def process(self, logits: torch.Tensor) -> Dict[str, Any]:
        try:
            return {"status": "success", "processed_logits": torch.sigmoid(logits)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
