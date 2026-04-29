# Omni SUR-Adapter Semantic Understanding
# Ref: Qrange-group/SUR-adapter — ACM MM'23 Oral
import math
from typing import List, Dict
def compute_clip_score(img_emb: List[float], txt_emb: List[float]) -> float:
    dot = sum(a*b for a, b in zip(img_emb, txt_emb))
    na = math.sqrt(sum(a*a for a in img_emb)) or 1; nb = math.sqrt(sum(b*b for b in txt_emb)) or 1
    return round(dot/(na*nb), 8)
def adapter_loss(original_clip: float, adapted_clip: float) -> float:
    return round(max(0, original_clip - adapted_clip), 6)
