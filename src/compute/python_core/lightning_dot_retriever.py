import torch
from typing import Dict, Any

class LightningRetriever:
    def __init__(self, index_tensor: torch.Tensor):
        self.index = index_tensor

    def retrieve(self, query: torch.Tensor, top_k: int = 5) -> Dict[str, Any]:
        try:
            scores = torch.matmul(self.index, query.t()).squeeze()
            top_scores, top_indices = torch.topk(scores, top_k)
            return {"status": "success", "indices": top_indices}
        except Exception as e:
            return {"status": "error", "message": str(e)}
