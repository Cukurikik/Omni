# Omni Rephrase-and-Respond Engine
# Ref: uclaml/Rephrase-and-Respond — MIT
from typing import Dict, List

def rephrase_prompt(question: str) -> str:
    return f"Rephrase and expand the question, then respond: {question}\nRephrased question:"

def one_step_rar(question: str) -> str:
    return f"{question}\nGiven the above question, first rephrase it, then respond."

def two_step_rar(question: str) -> Dict:
    return {"step1": f"Rephrase the following question: {question}",
            "step2": "Now answer the rephrased question above."}

def evaluate_rar(original_acc: float, rar_acc: float) -> Dict:
    improvement = rar_acc - original_acc
    return {"original": round(original_acc, 4), "rar": round(rar_acc, 4),
            "improvement": round(improvement, 4), "relative_gain": round(improvement / max(original_acc, 0.01), 4)}
