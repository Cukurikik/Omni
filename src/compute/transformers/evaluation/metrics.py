"""
OMNI Transformer — Metrics and Evaluation
Production evaluation metrics for NLP, vision, and generation tasks.
Learned from: mts-ai/OpenAutoNLU, seqeval patterns
"""
import torch
from typing import List, Dict, Any, Optional
from collections import Counter
import math
import logging

logger = logging.getLogger(__name__)


class ClassificationMetrics:
    """Precision, recall, F1 for classification tasks."""
    @staticmethod
    def compute(predictions: List[int], references: List[int], num_classes: int = 2) -> Dict[str, float]:
        tp = Counter()
        fp = Counter()
        fn = Counter()
        for pred, ref in zip(predictions, references):
            if pred == ref:
                tp[pred] += 1
            else:
                fp[pred] += 1
                fn[ref] += 1

        precision_per_class = {}
        recall_per_class = {}
        f1_per_class = {}
        for c in range(num_classes):
            p = tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) > 0 else 0.0
            r = tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) > 0 else 0.0
            f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
            precision_per_class[c] = p
            recall_per_class[c] = r
            f1_per_class[c] = f1

        accuracy = sum(tp.values()) / len(predictions) if predictions else 0.0
        macro_f1 = sum(f1_per_class.values()) / num_classes if num_classes > 0 else 0.0

        return {"accuracy": accuracy, "macro_f1": macro_f1, "precision": precision_per_class, "recall": recall_per_class, "f1": f1_per_class}


class NERMetrics:
    """Entity-level metrics for Named Entity Recognition."""
    @staticmethod
    def compute(pred_entities: List[List[Dict]], ref_entities: List[List[Dict]]) -> Dict[str, float]:
        tp, fp, fn_count = 0, 0, 0
        for preds, refs in zip(pred_entities, ref_entities):
            pred_set = {(e["start"], e["end"], e["label"]) for e in preds}
            ref_set = {(e["start"], e["end"], e["label"]) for e in refs}
            tp += len(pred_set & ref_set)
            fp += len(pred_set - ref_set)
            fn_count += len(ref_set - pred_set)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn_count) if (tp + fn_count) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        return {"precision": precision, "recall": recall, "f1": f1}


class PerplexityMetric:
    """Perplexity for language models."""
    @staticmethod
    def compute(losses: List[float]) -> float:
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        return math.exp(avg_loss) if avg_loss < 100 else float("inf")


class BLEUScore:
    """BLEU score for machine translation / text generation."""
    @staticmethod
    def compute(predictions: List[str], references: List[str], max_ngram: int = 4) -> float:
        def _ngrams(tokens, n):
            return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

        total_score = 0.0
        for pred, ref in zip(predictions, references):
            pred_tokens = pred.lower().split()
            ref_tokens = ref.lower().split()
            if not pred_tokens:
                continue
            scores = []
            for n in range(1, max_ngram + 1):
                pred_ng = Counter(_ngrams(pred_tokens, n))
                ref_ng = Counter(_ngrams(ref_tokens, n))
                matches = sum((pred_ng & ref_ng).values())
                total = sum(pred_ng.values())
                scores.append(matches / total if total > 0 else 0.0)

            if all(s > 0 for s in scores):
                log_avg = sum(math.log(s) for s in scores) / len(scores)
                bp = min(1.0, math.exp(1 - len(ref_tokens) / max(len(pred_tokens), 1)))
                total_score += bp * math.exp(log_avg)

        return total_score / max(len(predictions), 1)


class ROUGEScore:
    """ROUGE-L for summarization evaluation."""
    @staticmethod
    def compute(predictions: List[str], references: List[str]) -> Dict[str, float]:
        def _lcs_length(x, y):
            m, n = len(x), len(y)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    dp[i][j] = dp[i-1][j-1] + 1 if x[i-1] == y[j-1] else max(dp[i-1][j], dp[i][j-1])
            return dp[m][n]

        total_p, total_r, total_f = 0.0, 0.0, 0.0
        for pred, ref in zip(predictions, references):
            pred_tokens = pred.lower().split()
            ref_tokens = ref.lower().split()
            lcs = _lcs_length(pred_tokens, ref_tokens)
            p = lcs / len(pred_tokens) if pred_tokens else 0.0
            r = lcs / len(ref_tokens) if ref_tokens else 0.0
            f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
            total_p += p
            total_r += r
            total_f += f

        n = max(len(predictions), 1)
        return {"rouge_l_precision": total_p / n, "rouge_l_recall": total_r / n, "rouge_l_f1": total_f / n}
