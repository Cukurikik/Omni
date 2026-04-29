# Omni EditWorld Instruction Editor
# Compute: World dynamics simulation for instruction-following image editing.
# Ref: YangLing0818/EditWorld — ACM MM 2025
import math
from typing import Dict, List, Tuple

def compute_clip_alignment(img_emb: List[float], text_emb: List[float]) -> float:
    dot = sum(a * b for a, b in zip(img_emb, text_emb))
    na = math.sqrt(sum(a*a for a in img_emb)) or 1.0
    nb = math.sqrt(sum(b*b for b in text_emb)) or 1.0
    return round(dot / (na * nb), 8)

def evaluate_edit(original_clip: float, edited_clip: float) -> Dict:
    improvement = edited_clip - original_clip
    return {"original_alignment": original_clip, "edited_alignment": edited_clip,
            "improvement": round(improvement, 6), "success": improvement > 0}
