import numpy as np

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ConfidentLearning:
    def __init__(self):
        pass

    def compute_self_confidence_margins(self, pred_probs: list[list[float]], given_labels: list[int]) -> OmniResult:
        if not pred_probs or not given_labels:
            return OmniResult(error="Predictions and labels cannot be empty")
            
        if len(pred_probs) != len(given_labels):
            return OmniResult(error="Number of predictions must match number of labels")

        margins = []
        try:
            for probs, label in zip(pred_probs, given_labels):
                if label < 0 or label >= len(probs):
                    return OmniResult(error=f"Label {label} out of bounds for prediction array size {len(probs)}")
                
                # Self-confidence is the predicted probability of the given label
                self_conf = probs[label]
                
                # Margin: Difference between self-confidence and the maximum probability of any OTHER class
                other_probs = [p for i, p in enumerate(probs) if i != label]
                max_other = max(other_probs) if other_probs else 0.0
                
                margin = self_conf - max_other
                margins.append(margin)

            return OmniResult(value=margins)
        except Exception as e:
            return OmniResult(error=str(e))
