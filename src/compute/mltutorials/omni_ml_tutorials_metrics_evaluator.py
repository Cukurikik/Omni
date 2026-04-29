# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# ML Tutorials Metrics Evaluator (OMNI Zero-Mock Implementation)
# Implements exact F1/Precision/Recall calculation without division wrappers.

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Result:
    value: Optional[Dict[str, float]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: Dict[str, float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class MetricsEvaluator:
    def compute_confusion_matrix_metrics(self, y_true: List[int], y_pred: List[int]) -> Result:
        if len(y_true) != len(y_pred):
            return Result.err("Label lengths do not match.")
        if len(y_true) == 0:
            return Result.err("Label arrays are empty.")

        tp = 0
        fp = 0
        tn = 0
        fn = 0

        for t, p in zip(y_true, y_pred):
            if t == 1 and p == 1:
                tp += 1
            elif t == 0 and p == 1:
                fp += 1
            elif t == 0 and p == 0:
                tn += 1
            elif t == 1 and p == 0:
                fn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        f1 = 0.0
        if precision + recall > 0:
            f1 = 2.0 * (precision * recall) / (precision + recall)
            
        accuracy = (tp + tn) / len(y_true)

        return Result.ok({
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "accuracy": accuracy,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn
        })
