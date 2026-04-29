# Omni AI4Education Assessment Engine
# Ref: GeminiLight/awesome-ai-llm4education
from typing import List, Dict

def assess_question_difficulty(question: str, n_concepts: int = 0) -> Dict:
    words = len(question.split()); complexity = min(1.0, (words / 50 + n_concepts * 0.1))
    level = "hard" if complexity > 0.7 else "medium" if complexity > 0.4 else "easy"
    return {"complexity": round(complexity, 4), "level": level, "n_concepts": n_concepts}

def adaptive_feedback(score: float, topic: str) -> str:
    if score >= 0.8: return f"Excellent work on {topic}! Consider advanced topics."
    elif score >= 0.5: return f"Good progress on {topic}. Review key concepts for improvement."
    return f"Let's revisit {topic} fundamentals. Focus on core principles."

def learning_progress(scores: List[float]) -> Dict:
    if not scores: return {"trend": "none", "avg": 0}
    avg = sum(scores)/len(scores)
    trend = "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable"
    return {"avg": round(avg, 4), "trend": trend, "n_assessments": len(scores)}
