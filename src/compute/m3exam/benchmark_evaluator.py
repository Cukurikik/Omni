class M3ExamEvaluator:
    def __init__(self):
        self.metrics = ["accuracy", "multilingual_f1", "multimodal_score"]
        
    def evaluate_model(self, predictions: dict, ground_truth: dict) -> dict:
        correct = sum(1 for k, v in predictions.items() if k in ground_truth and v == ground_truth[k])
        total = len(ground_truth)
        return {
            "accuracy": correct / total if total > 0 else 0.0
        }
