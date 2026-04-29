# Omni Shot2Story Video Understanding Engine
# Ref: bytedance/Shot2Story — video captioning
from typing import List, Dict

def detect_shot_boundaries(frame_diffs: List[float], threshold: float = 0.5) -> List[int]:
    return [i for i, d in enumerate(frame_diffs) if d > threshold]

def shot_level_caption(shots: List[Dict]) -> List[Dict]:
    return [{"shot_id": i, "start": s.get("start",0), "end": s.get("end",0), "caption": s.get("text","")} for i, s in enumerate(shots)]

def video_summary(shot_captions: List[str]) -> str:
    return " ".join(shot_captions[:20])

def evaluate_captioning(preds: List[str], refs: List[str]) -> Dict:
    scores = []
    for p, r in zip(preds, refs):
        pt = set(p.lower().split()); rt = set(r.lower().split())
        tp = len(pt & rt); pr = tp/max(len(pt),1); rc = tp/max(len(rt),1)
        f1 = 2*pr*rc/max(pr+rc, 1e-8)
        scores.append(f1)
    return {"mean_f1": round(sum(scores)/max(len(scores),1), 4)}
