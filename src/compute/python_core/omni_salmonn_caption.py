# Omni Video-SALMONN-2 Audio-Visual Caption Engine
# Ref: bytedance/video-SALMONN-2 — Apache-2.0
import math
from typing import List, Dict

def audio_visual_align_score(audio_feats: List[float], visual_feats: List[float]) -> float:
    dot = sum(a*v for a, v in zip(audio_feats, visual_feats))
    na = math.sqrt(sum(a**2 for a in audio_feats)) or 1; nv = math.sqrt(sum(v**2 for v in visual_feats)) or 1
    return round(dot / (na * nv), 4)

def temporal_grounding(events: List[Dict], duration: float) -> List[Dict]:
    return [{"event": e["text"], "start_pct": round(e.get("start",0)/max(duration,1)*100,1), "end_pct": round(e.get("end",0)/max(duration,1)*100,1)} for e in events]

def caption_quality(caption: str, reference: str) -> Dict:
    ct = set(caption.lower().split()); rt = set(reference.lower().split())
    tp = len(ct & rt); p = tp/max(len(ct),1); r = tp/max(len(rt),1)
    f1 = 2*p*r/max(p+r, 1e-8)
    return {"rouge_l_approx": round(f1, 4), "length": len(caption.split())}
