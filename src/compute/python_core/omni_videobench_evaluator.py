# Omni VideoBench Evaluator
# Compute: Video LLM benchmark evaluation.
# Ref: PKU-YuanGroup/Video-Bench
from typing import Dict, List

def accuracy(predictions: List[str], ground_truths: List[str]) -> float:
    if not predictions or len(predictions) != len(ground_truths):
        return 0.0
    correct = sum(1 for p, g in zip(predictions, ground_truths) if p.strip().lower() == g.strip().lower())
    return round(correct / len(predictions), 6)

def evaluate_video_qa(results: List[Dict]) -> Dict:
    by_category = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = {"preds": [], "gts": []}
        by_category[cat]["preds"].append(r.get("prediction", ""))
        by_category[cat]["gts"].append(r.get("ground_truth", ""))
    scores = {cat: accuracy(v["preds"], v["gts"]) for cat, v in by_category.items()}
    overall = sum(scores.values()) / len(scores) if scores else 0.0
    return {"category_scores": scores, "overall": round(overall, 6)}
