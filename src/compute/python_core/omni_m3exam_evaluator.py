# Omni M3Exam Multilingual Evaluator
# Ref: DAMO-NLP-SG/M3Exam
from typing import List, Dict

LANGUAGES = ["en", "zh", "id", "th", "vi", "pt", "it", "af", "jv"]
LEVELS = ["primary", "middle", "high"]

def evaluate_mcq(prediction: str, answer: str) -> bool:
    return prediction.strip().upper() == answer.strip().upper()

def batch_evaluate(results: List[Dict]) -> Dict:
    by_lang, by_level = {}, {}
    for r in results:
        lang = r.get("language", "en"); level = r.get("level", "high")
        correct = evaluate_mcq(r.get("prediction", ""), r.get("answer", ""))
        by_lang.setdefault(lang, []).append(correct)
        by_level.setdefault(level, []).append(correct)
    return {"by_language": {l: round(sum(v)/max(len(v),1), 4) for l, v in by_lang.items()},
            "by_level": {l: round(sum(v)/max(len(v),1), 4) for l, v in by_level.items()},
            "overall": round(sum(evaluate_mcq(r.get("prediction",""), r.get("answer","")) for r in results) / max(len(results),1), 4)}
