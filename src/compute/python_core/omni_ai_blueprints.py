# Omni AI Blueprints Pipeline Runner
# Ref: HPInc/AI-Blueprints — MIT
from typing import List, Dict

def build_pipeline(steps: List[Dict]) -> Dict:
    validated = []
    for step in steps:
        if "name" not in step or "type" not in step:
            continue
        validated.append({"name": step["name"], "type": step["type"],
                         "params": step.get("params", {}), "status": "ready"})
    return {"pipeline_id": f"bp-{len(validated)}", "steps": validated, "n_steps": len(validated)}

def run_data_prep(data: List[Dict], columns: List[str]) -> List[Dict]:
    return [{c: row.get(c) for c in columns} for row in data]

def compute_experiment_metrics(y_true: List[int], y_pred: List[int]) -> Dict:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
