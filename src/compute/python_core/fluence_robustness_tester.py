import torch
from typing import Dict, Any

class RobustnessTester:
    def add_noise(self, embeddings: torch.Tensor, noise_level: float = 0.01) -> Dict[str, Any]:
        try:
            noise = torch.randn_like(embeddings) * noise_level
            return {"status": "success", "noisy_embeddings": embeddings + noise}
        except Exception as e:
            return {"status": "error", "message": str(e)}
