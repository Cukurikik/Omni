from typing import List

class RAGEvaluatorMRR:
    def compute_mrr(self, rank_positions: List[int]) -> float:
        if not rank_positions:
            return 0.0
        score = sum(1.0 / r for r in rank_positions if r > 0)
        return score / len(rank_positions)
