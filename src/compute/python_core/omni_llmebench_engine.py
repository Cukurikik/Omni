# Omni LLMeBench Benchmark Engine
# Ref: qcri/LLMeBench
from typing import List, Dict

def evaluate_task(prediction: str, ground_truth: str, metric: str = "exact_match") -> float:
    if metric == "exact_match":
        return 1.0 if prediction.strip() == ground_truth.strip() else 0.0
    if metric == "f1":
        p_set = set(prediction.lower().split()); g_set = set(ground_truth.lower().split())
        if not g_set: return 0.0
        precision = len(p_set & g_set) / max(len(p_set), 1)
        recall = len(p_set & g_set) / len(g_set)
        return round(2 * precision * recall / max(precision + recall, 1e-9), 4)
    return 0.0

def aggregate_multilingual(results: List[Dict]) -> Dict:
    by_lang: Dict[str, List] = {}
    for r in results:
        by_lang.setdefault(r.get("lang", "en"), []).append(r.get("score", 0))
    return {l: round(sum(v)/max(len(v),1), 4) for l, v in by_lang.items()}

def prompt_template(task: str, input_text: str, n_shots: int = 0) -> str:
    prefix = f"Task: {task}\n"
    if n_shots > 0: prefix += f"[{n_shots}-shot examples would be here]\n"
    return prefix + f"Input: {input_text}\nOutput:"
