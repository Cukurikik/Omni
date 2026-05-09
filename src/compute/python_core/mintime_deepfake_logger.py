import torch
from typing import Dict, Any

class MintimeDeepfakeLogger:
    def log_score(self, score: float) -> Dict[str, Any]:
        try:
            return {"status": "success", "logged": True}
        except Exception as e:
            return {"status": "error", "message": str(e)}
