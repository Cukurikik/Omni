class M3F1Scorer:
    def compute_f1(self, precision: float, recall: float) -> float:
        if precision < 0 or recall < 0:
            raise ValueError("Metrics must be positive")
        if precision + recall == 0:
            return 0.0
        return 2.0 * (precision * recall) / (precision + recall)
