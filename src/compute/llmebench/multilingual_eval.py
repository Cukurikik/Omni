from sklearn.metrics import accuracy_score, f1_score
from typing import List

class LLMeBenchEvaluator:
    def __init__(self):
        pass
        
    def evaluate_task(self, y_true: List[str], y_pred: List[str]) -> dict:
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average='macro')
        return {
            "accuracy": acc,
            "macro_f1": f1
        }
