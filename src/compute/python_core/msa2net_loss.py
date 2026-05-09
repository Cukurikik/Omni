import torch
from typing import Dict, Any

class MSA2NetLoss:
    def compute(self, preds: torch.Tensor, targets: torch.Tensor) -> Dict[str, Any]:
        try:
            return {"status": "success", "loss": torch.nn.functional.cross_entropy(preds, targets)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
