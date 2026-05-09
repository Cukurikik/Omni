import torch
from typing import Dict, Any

class TransframerContextSampler:
    def sample(self, frames: torch.Tensor) -> Dict[str, Any]:
        try:
            return {"status": "success", "sampled_frames": frames[:, ::2]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
