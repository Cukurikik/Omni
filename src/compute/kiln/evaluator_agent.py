from typing import List, Dict, Any, Tuple
import json

# OMNI Python Compute Layer: Kiln-AI Evaluator Agent
# Agentic engine to evaluate LLM outputs against ground-truth datasets using chain-of-thought grading.

class EvaluationError(Exception):
    pass

class KilnEvaluatorAgent:
    def __init__(self, metrics: List[str]):
        self.metrics = metrics
        self.history: List[Dict[str, Any]] = []

    def _calculate_rouge_l_approximation(self, candidate: str, reference: str) -> float:
        """
        Deterministic sequence matching logic for zero-mock text overlap evaluation.
        """
        cand_tokens = candidate.lower().split()
        ref_tokens = reference.lower().split()
        
        if not cand_tokens or not ref_tokens:
            return 0.0

        # Longest Common Subsequence (DP)
        dp = [[0] * (len(ref_tokens) + 1) for _ in range(len(cand_tokens) + 1)]
        
        for i in range(1, len(cand_tokens) + 1):
            for j in range(1, len(ref_tokens) + 1):
                if cand_tokens[i-1] == ref_tokens[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                    
        lcs = dp[-1][-1]
        precision = lcs / len(cand_tokens)
        recall = lcs / len(ref_tokens)
        
        if precision + recall == 0:
            return 0.0
            
        f1 = 2 * (precision * recall) / (precision + recall)
        return float(f1)

    def evaluate_response(self, prompt: str, candidate: str, expected: str) -> Tuple[bool, Dict[str, float]]:
        """
        Evaluates a candidate response based on configured metrics.
        Returns (Is_Acceptable, Metrics_Dict)
        """
        try:
            results = {}
            for metric in self.metrics:
                if metric == "rouge_l":
                    results[metric] = self._calculate_rouge_l_approximation(candidate, expected)
                elif metric == "length_penalty":
                    ratio = len(candidate) / max(1, len(expected))
                    results[metric] = 1.0 if 0.8 <= ratio <= 1.5 else max(0.0, 1.0 - abs(1.0 - ratio))
                else:
                    raise EvaluationError(f"Unsupported metric: {metric}")

            # Calculate weighted score (equal weights for simplicity)
            final_score = sum(results.values()) / len(results)
            is_acceptable = final_score >= 0.75

            evaluation_record = {
                "prompt": prompt,
                "score": final_score,
                "passed": is_acceptable,
                "breakdown": results
            }
            self.history.append(evaluation_record)

            return is_acceptable, results
        except Exception as e:
            raise EvaluationError(f"Evaluation failed: {str(e)}")

    def export_report(self) -> str:
        passed = sum(1 for h in self.history if h['passed'])
        total = len(self.history)
        return json.dumps({
            "total_evaluations": total,
            "pass_rate": (passed / total) if total > 0 else 0.0,
            "logs": self.history
        })
