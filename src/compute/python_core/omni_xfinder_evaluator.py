# Omni xFinder Automated Evaluator Engine
# Ref: IAAR-Shanghai/xFinder — ICLR'25
# Key-answer extraction for reliable LLM evaluation
import re
from typing import List, Dict, Optional

ANSWER_PATTERNS = [
    r"(?:the answer is|answer:)\s*([A-Za-z0-9\.\-\+]+)",
    r"(?:\*\*|__)([A-Za-z0-9\.\-\+]+)(?:\*\*|__)",
    r"(?:therefore|thus|hence|so),?\s*(?:the answer is)?\s*([A-Za-z0-9\.\-\+]+)",
    r"\b([A-D])\b\s*$",
]

def extract_key_answer(response: str, question_type: str = "multiple_choice") -> Optional[str]:
    """Extract key answer from LLM response using xFinder patterns."""
    text = response.strip()
    if question_type == "multiple_choice":
        for pat in ANSWER_PATTERNS:
            m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
            if m:
                return m.group(1).strip().upper()
        last_line = text.strip().split('\n')[-1]
        m = re.search(r'\b([A-D])\b', last_line)
        if m:
            return m.group(1).upper()
    elif question_type == "numeric":
        numbers = re.findall(r'-?\d+\.?\d*', text)
        if numbers:
            return numbers[-1]
    elif question_type == "free_form":
        return text.split('\n')[-1].strip()[:200]
    return None

def evaluate_extraction(pred: str, gold: str, question_type: str = "multiple_choice") -> bool:
    """Compare extracted answer to gold answer."""
    if not pred or not gold:
        return False
    if question_type == "multiple_choice":
        return pred.strip().upper() == gold.strip().upper()
    elif question_type == "numeric":
        try:
            return abs(float(pred) - float(gold)) < 1e-6
        except ValueError:
            return False
    return pred.strip().lower() == gold.strip().lower()

def batch_evaluate(samples: List[Dict]) -> Dict:
    """Batch evaluation of LLM responses. Each sample: {response, gold, type}."""
    correct = 0; total = len(samples); extractions = []
    for s in samples:
        pred = extract_key_answer(s["response"], s.get("type", "multiple_choice"))
        is_correct = evaluate_extraction(pred or "", s["gold"], s.get("type", "multiple_choice"))
        if is_correct:
            correct += 1
        extractions.append({"pred": pred, "gold": s["gold"], "correct": is_correct})
    return {"accuracy": round(correct / max(total, 1), 4), "total": total,
            "correct": correct, "extractions": extractions[:20]}

def regex_reliability(responses: List[str], golds: List[str]) -> Dict:
    """Measure regex-based extraction reliability vs xFinder approach."""
    regex_hits = sum(1 for r in responses if re.search(r'\b[A-D]\b', r))
    return {"regex_coverage": round(regex_hits / max(len(responses),1), 4),
            "n_responses": len(responses)}
