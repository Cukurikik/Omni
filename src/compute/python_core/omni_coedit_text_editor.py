# Omni CoEdIT Text Editor
# Compute Layer: Task-specific instruction tuning for text editing.
# Ref: vipulraheja/coedit — EMNLP 2023
import hashlib
from typing import Dict, List

EDIT_TASKS = {"grammar", "simplify", "paraphrase", "coherence", "formality", "neutralize"}

def classify_edit_instruction(instruction: str) -> str:
    lower = instruction.lower()
    for task in ["grammar", "simpl", "paraphrase", "coheren", "formal", "neutral"]:
        if task in lower:
            return task if task in EDIT_TASKS else "paraphrase"
    return "paraphrase"

def compute_edit_distance(source: str, target: str) -> int:
    n, m = len(source), len(target)
    dp = list(range(m + 1))
    for i in range(1, n + 1):
        prev = dp[0]; dp[0] = i
        for j in range(1, m + 1):
            temp = dp[j]
            dp[j] = prev if source[i-1] == target[j-1] else 1 + min(prev, dp[j], dp[j-1])
            prev = temp
    return dp[m]

def edit_quality_score(source: str, edited: str) -> Dict:
    dist = compute_edit_distance(source, edited)
    mx = max(len(source), len(edited), 1)
    return {"edit_distance": dist, "conservation": round(1.0 - dist / mx, 6)}
