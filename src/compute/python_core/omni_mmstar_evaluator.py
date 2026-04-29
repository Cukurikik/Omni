# Omni MMStar Vision-Language Evaluator
# Ref: MMStar-Benchmark/MMStar — NeurIPS 2024
from typing import List, Dict

CAPABILITIES = ["coarse_perception", "fine_grained_perception", "instance_reasoning",
                 "logical_reasoning", "science_technology", "math"]

def evaluate_vqa(prediction: str, answer: str) -> bool:
    return prediction.strip().upper() == answer.strip().upper()

def detect_data_leakage(question: str, model_response_no_image: str, answer: str) -> bool:
    return model_response_no_image.strip().upper() == answer.strip().upper()

def filter_coarse_perception(items: List[Dict]) -> List[Dict]:
    return [item for item in items if not detect_data_leakage(
        item.get("question", ""), item.get("text_only_response", ""), item.get("answer", ""))]

def aggregate_by_capability(results: List[Dict]) -> Dict:
    by_cap = {}
    for r in results:
        cap = r.get("capability", "unknown")
        by_cap.setdefault(cap, []).append(evaluate_vqa(r.get("prediction", ""), r.get("answer", "")))
    return {c: round(sum(v)/max(len(v),1), 4) for c, v in by_cap.items()}
