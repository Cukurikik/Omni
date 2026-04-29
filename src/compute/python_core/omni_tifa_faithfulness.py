# Omni TIFA Faithfulness Evaluation Engine
# Ref: Yushi-Hu/tifa — Apache-2.0 | ICCV'23
# Text-to-Image Faithfulness via VQA decomposition
import math
from typing import List, Dict, Tuple

def decompose_prompt_to_questions(prompt: str) -> List[Dict]:
    """Decompose a text prompt into binary VQA questions for faithfulness eval."""
    words = prompt.lower().split()
    entities = [w for w in words if len(w) > 3 and w.isalpha()]
    questions = []
    for i, entity in enumerate(entities[:10]):
        questions.append({
            "id": i, "element": entity, "element_type": "object",
            "question": f"Is there a {entity} in the image?",
            "choices": ["yes", "no"], "expected": "yes"
        })
    adjectives = [w for w in words if w.endswith(("red","blue","green","big","small","tall","old","new"))]
    for j, adj in enumerate(adjectives[:5]):
        questions.append({
            "id": len(questions), "element": adj, "element_type": "attribute",
            "question": f"Is the object {adj}?", "choices": ["yes","no"], "expected": "yes"
        })
    return questions

def compute_tifa_score(answers: List[Dict]) -> Dict:
    """Compute TIFA score from VQA answers. Each answer has 'correct': bool."""
    if not answers:
        return {"tifa_score": 0.0, "n_questions": 0, "n_correct": 0}
    n_correct = sum(1 for a in answers if a.get("correct", False))
    return {
        "tifa_score": round(n_correct / len(answers), 4),
        "n_questions": len(answers), "n_correct": n_correct
    }

def element_wise_score(answers: List[Dict]) -> Dict[str, float]:
    """Per-element-type breakdown of faithfulness."""
    buckets: Dict[str, List[bool]] = {}
    for a in answers:
        et = a.get("element_type", "unknown")
        buckets.setdefault(et, []).append(a.get("correct", False))
    return {k: round(sum(v)/max(len(v),1), 4) for k, v in buckets.items()}

def batch_tifa(prompts_answers: List[Tuple[str, List[Dict]]]) -> Dict:
    """Batch TIFA evaluation across multiple prompt-image pairs."""
    scores = [compute_tifa_score(ans)["tifa_score"] for _, ans in prompts_answers]
    return {
        "mean_tifa": round(sum(scores)/max(len(scores),1), 4),
        "min_tifa": round(min(scores) if scores else 0, 4),
        "max_tifa": round(max(scores) if scores else 0, 4),
        "n_samples": len(scores)
    }
