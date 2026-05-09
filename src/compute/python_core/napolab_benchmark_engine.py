import torch
from typing import Dict, Any, List

class NapolabBenchmarkEngine:
    """
    Napolab: Natural Portuguese Language Benchmark Evaluator.
    """
    def __init__(self):
        self.supported_tasks = ["QA", "Sentiment", "NLI"]
        
    def evaluate_model(self, model_outputs: List[str], ground_truth: List[str], task: str) -> Dict[str, Any]:
        try:
            if task not in self.supported_tasks:
                raise ValueError(f"Task {task} not supported by Napolab.")
                
            correct = sum(1 for p, g in zip(model_outputs, ground_truth) if p.strip() == g.strip())
            accuracy = correct / len(ground_truth) if ground_truth else 0.0
            
            return {
                "status": "success",
                "task": task,
                "accuracy": accuracy,
                "total_evaluated": len(ground_truth)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
