"""
OMNI Compute — Evaluation Harness
Multi-benchmark evaluation for language models (lm-eval inspired).
"""
import logging, time, json, os, hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Tuple

logger = logging.getLogger("omni.eval")

@dataclass
class EvalTask:
    name: str; dataset: List[Dict]; metric: str = "accuracy"
    num_fewshot: int = 0; description: str = ""

@dataclass
class EvalResult:
    task_name: str; metric: str; score: float; stderr: float = 0.0
    num_examples: int = 0; duration_sec: float = 0.0

class OmniEvalHarness:
    """Multi-benchmark evaluation harness for LLMs."""
    def __init__(self, model_fn: Optional[Callable] = None):
        self.model_fn = model_fn; self.tasks: Dict[str, EvalTask] = {}
        self.results: List[EvalResult] = []

    def register_task(self, task: EvalTask):
        self.tasks[task.name] = task
        logger.info(f"Task registered: {task.name} ({len(task.dataset)} examples)")

    def register_mmlu(self, data: List[Dict]):
        self.register_task(EvalTask("mmlu", data, "accuracy", 5, "Massive Multitask Language Understanding"))

    def register_humaneval(self, data: List[Dict]):
        self.register_task(EvalTask("humaneval", data, "pass@1", 0, "Code generation"))

    def register_gsm8k(self, data: List[Dict]):
        self.register_task(EvalTask("gsm8k", data, "exact_match", 8, "Grade school math"))

    def register_truthfulqa(self, data: List[Dict]):
        self.register_task(EvalTask("truthfulqa", data, "mc2", 0, "Truthful QA"))

    def _compute_accuracy(self, predictions: List[str], references: List[str]) -> Tuple[float, float]:
        correct = sum(1 for p, r in zip(predictions, references) if p.strip().lower() == r.strip().lower())
        n = max(len(predictions), 1)
        acc = correct / n
        import math
        stderr = math.sqrt(acc * (1 - acc) / n) if n > 1 else 0.0
        return acc, stderr

    def _compute_exact_match(self, predictions: List[str], references: List[str]) -> Tuple[float, float]:
        def extract_number(s):
            import re
            nums = re.findall(r'-?\d+\.?\d*', s)
            return nums[-1] if nums else s.strip()
        correct = sum(1 for p, r in zip(predictions, references) if extract_number(p) == extract_number(r))
        n = max(len(predictions), 1)
        em = correct / n
        import math
        return em, math.sqrt(em * (1 - em) / n) if n > 1 else 0.0

    def evaluate_task(self, task_name: str) -> EvalResult:
        task = self.tasks.get(task_name)
        if not task: raise ValueError(f"Task {task_name} not registered")
        start = time.time()
        predictions, references = [], []
        for example in task.dataset:
            prompt = example.get("prompt", example.get("question", ""))
            ref = example.get("answer", example.get("target", ""))
            if self.model_fn:
                pred = self.model_fn(prompt)
            else:
                pred = ref  # passthrough for testing
            predictions.append(pred); references.append(ref)
        if task.metric == "accuracy":
            score, stderr = self._compute_accuracy(predictions, references)
        elif task.metric in ("exact_match", "pass@1"):
            score, stderr = self._compute_exact_match(predictions, references)
        else:
            score, stderr = self._compute_accuracy(predictions, references)
        duration = time.time() - start
        result = EvalResult(task_name, task.metric, round(score, 4), round(stderr, 4), len(task.dataset), round(duration, 2))
        self.results.append(result)
        logger.info(f"{task_name}: {task.metric}={score:.4f} ± {stderr:.4f} ({duration:.1f}s)")
        return result

    def evaluate_all(self) -> List[EvalResult]:
        return [self.evaluate_task(name) for name in self.tasks]

    def get_leaderboard(self) -> Dict:
        scores = {r.task_name: r.score for r in self.results}
        avg = sum(scores.values()) / max(len(scores), 1)
        return {"tasks": scores, "average": round(avg, 4), "num_tasks": len(scores)}

    def save_results(self, path: str):
        data = {"results": [vars(r) for r in self.results], "leaderboard": self.get_leaderboard()}
        with open(path, "w") as f: json.dump(data, f, indent=2)
