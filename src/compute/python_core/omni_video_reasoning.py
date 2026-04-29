# Omni Video Reasoning Landscape Engine
# Ref: LJungang/Awesome-Video-Reasoning-Landscape
from typing import List, Dict

def temporal_reasoning_score(pred_events: List[str], gold_events: List[str]) -> float:
    correct = sum(1 for p, g in zip(pred_events, gold_events) if p.strip().lower() == g.strip().lower())
    return round(correct / max(len(gold_events), 1), 4)

def chain_of_frames_eval(frame_descriptions: List[str], question: str, answer: str) -> Dict:
    relevant = sum(1 for f in frame_descriptions if any(w in f.lower() for w in question.lower().split()))
    return {"relevant_frames": relevant, "total_frames": len(frame_descriptions), "coverage": round(relevant/max(len(frame_descriptions),1), 4)}

def streaming_video_accuracy(predictions: List[Dict]) -> Dict:
    correct = sum(1 for p in predictions if p.get("correct", False))
    return {"accuracy": round(correct/max(len(predictions),1), 4), "latency_avg_ms": round(sum(p.get("latency_ms",0) for p in predictions)/max(len(predictions),1), 1)}
