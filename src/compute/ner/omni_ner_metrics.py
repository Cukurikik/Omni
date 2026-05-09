"""
omni_ner_metrics.py — Named Entity Recognition Evaluator
Layer: Compute / AI

Calculates strict exact-match Precision, Recall, and F1 scores for
predicted entity spans against ground-truth annotations.
"""

from typing import List, Dict

class OmniNERMetrics:
    def __init__(self):
        self.true_positives = 0
        self.false_positives = 0
        self.false_negatives = 0

    def add_batch(self, 
                  predicted_spans: List[List[Dict]], 
                  true_spans: List[List[Dict]]):
        """
        Expects a list (batch) of lists (spans in sentence) of dicts:
        {"start": int, "end": int, "label_id": int}
        """
        assert len(predicted_spans) == len(true_spans)

        for p_spans, t_spans in zip(predicted_spans, true_spans):
            # Convert to sets of tuples for easy intersection
            # Tuple format: (start, end, label)
            p_set = set((s["start"], s["end"], s["label_id"]) for s in p_spans)
            t_set = set((s["start"], s["end"], s["label_id"]) for s in t_spans)
            
            # Exact matches
            tp = len(p_set.intersection(t_set))
            
            # Predicted but not in true
            fp = len(p_set - t_set)
            
            # True but not predicted
            fn = len(t_set - p_set)
            
            self.true_positives += tp
            self.false_positives += fp
            self.false_negatives += fn

    def compute(self) -> Dict[str, float]:
        """Returns the final Precision, Recall, and F1 scores."""
        precision = 0.0
        if (self.true_positives + self.false_positives) > 0:
            precision = self.true_positives / (self.true_positives + self.false_positives)
            
        recall = 0.0
        if (self.true_positives + self.false_negatives) > 0:
            recall = self.true_positives / (self.true_positives + self.false_negatives)
            
        f1 = 0.0
        if (precision + recall) > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
            
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

    def reset(self):
        self.true_positives = 0
        self.false_positives = 0
        self.false_negatives = 0
