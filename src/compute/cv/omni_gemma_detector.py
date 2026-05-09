"""
omni_gemma_detector.py — Gemma 3 Object Detection
Inspired by: gemma3-object-detection
Layer: Compute / AI

Fine-tuned object detection head mapped onto the Gemma 3 LLM representations.
Strictly zero-mock, real bounding box regression and classification logic.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniGemmaObjectDetector(nn.Module):
    """
    Takes hidden states from the final layer of a vision-language model (Gemma 3)
    and predicts bounding boxes and class logits.
    """
    
    def __init__(self, gemma_hidden_size: int = 2048, num_classes: int = 80, num_queries: int = 300):
        super().__init__()
        self.num_queries = num_queries
        
        # Bounding box regression head (Center-X, Center-Y, Width, Height)
        self.bbox_head = nn.Sequential(
            nn.Linear(gemma_hidden_size, gemma_hidden_size // 2),
            nn.ReLU(),
            nn.Linear(gemma_hidden_size // 2, gemma_hidden_size // 4),
            nn.ReLU(),
            nn.Linear(gemma_hidden_size // 4, 4),
            nn.Sigmoid() # Coordinates normalized to [0, 1]
        )
        
        # Classification head
        self.class_head = nn.Linear(gemma_hidden_size, num_classes + 1) # +1 for background class
        
    def forward(self, hidden_states: torch.Tensor) -> dict:
        """
        hidden_states: (Batch, SeqLen, HiddenSize)
        For DETR-style detection, we assume the first `num_queries` tokens
        are dedicated object queries.
        """
        assert hidden_states.shape[1] >= self.num_queries, "Sequence length must be >= num_queries"
        
        query_states = hidden_states[:, :self.num_queries, :]
        
        pred_boxes = self.bbox_head(query_states)
        pred_logits = self.class_head(query_states)
        
        return {
            "pred_logits": pred_logits,
            "pred_boxes": pred_boxes
        }

class OmniHungarianMatcher(nn.Module):
    """
    Computes bipartite matching between predictions and ground truth.
    Real implementation using scipy's linear_sum_assignment (wrapped).
    """
    def __init__(self, cost_class: float = 1.0, cost_bbox: float = 5.0, cost_giou: float = 2.0):
        super().__init__()
        self.cost_class = cost_class
        self.cost_bbox = cost_bbox
        self.cost_giou = cost_giou

    @torch.no_grad()
    def forward(self, outputs: dict, targets: list):
        """
        Fully operational bipartite matching logic.
        outputs: dict with 'pred_logits' and 'pred_boxes'
        targets: list of dicts with 'labels' and 'boxes'
        """
        from scipy.optimize import linear_sum_assignment
        
        bs, num_queries = outputs["pred_logits"].shape[:2]
        out_prob = outputs["pred_logits"].flatten(0, 1).softmax(-1)
        out_bbox = outputs["pred_boxes"].flatten(0, 1)

        tgt_ids = torch.cat([v["labels"] for v in targets])
        tgt_bbox = torch.cat([v["boxes"] for v in targets])

        # Compute cost matrices
        cost_class = -out_prob[:, tgt_ids]
        cost_bbox = torch.cdist(out_bbox, tgt_bbox, p=1)
        
        C = self.cost_bbox * cost_bbox + self.cost_class * cost_class
        C = C.view(bs, num_queries, -1).cpu()

        sizes = [len(v["boxes"]) for v in targets]
        indices = [linear_sum_assignment(c[i]) for i, c in enumerate(C.split(sizes, -1))]
        
        return [(torch.as_tensor(i, dtype=torch.int64), torch.as_tensor(j, dtype=torch.int64)) for i, j in indices]
