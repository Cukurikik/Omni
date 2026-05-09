"""
@omni-layer Compute | @omni-source hiyouga/Dual-Contrastive-Learning
@omni-description Dual Contrastive Learning for text classification: unsupervised and 
supervised contrastive objectives with label-aware augmentation.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniDualContrastiveLearning:
    """Dual CL: instance-level + label-level contrastive objectives."""
    def __init__(self, d_model: int = 768, n_labels: int = 5, temperature: float = 0.07):
        self.d_model = d_model
        self.n_labels = n_labels
        self.temperature = temperature
        self.label_embeddings = [[math.sin((i+1)*(j+1)*0.005) for j in range(d_model)] for i in range(n_labels)]

    def _cosine_sim(self, a: List[float], b: List[float]) -> float:
        d = min(len(a), len(b))
        dot = sum(a[i]*b[i] for i in range(d))
        na = math.sqrt(sum(a[i]**2 for i in range(d)) + 1e-8)
        nb = math.sqrt(sum(b[i]**2 for i in range(d)) + 1e-8)
        return dot / (na * nb)

    def instance_contrastive_loss(self, embeddings: List[List[float]], labels: List[int]) -> OmniResult:
        try:
            n = len(embeddings)
            if n < 2:
                return OmniResult(error=Exception("Need >= 2 samples"))
            total_loss = 0.0
            count = 0
            for i in range(n):
                positives = [j for j in range(n) if j != i and labels[j] == labels[i]]
                if not positives:
                    continue
                for p in positives:
                    sim_pos = self._cosine_sim(embeddings[i], embeddings[p]) / self.temperature
                    exp_sum = sum(math.exp(self._cosine_sim(embeddings[i], embeddings[j]) / self.temperature - sim_pos) for j in range(n) if j != i)
                    total_loss += math.log(1.0 + exp_sum)
                    count += 1
            return OmniResult(data={"instance_loss": total_loss / max(count, 1), "n_pairs": count})
        except Exception as e:
            return OmniResult(error=Exception(f"Instance CL failed: {e}"))

    def label_contrastive_loss(self, embeddings: List[List[float]], labels: List[int]) -> OmniResult:
        try:
            n = len(embeddings)
            total_loss = 0.0
            for i in range(n):
                label = labels[i] % self.n_labels
                pos_sim = self._cosine_sim(embeddings[i], self.label_embeddings[label]) / self.temperature
                neg_sims = [self._cosine_sim(embeddings[i], self.label_embeddings[j]) / self.temperature for j in range(self.n_labels) if j != label]
                max_neg = max(neg_sims) if neg_sims else 0
                exp_neg = sum(math.exp(ns - max_neg) for ns in neg_sims)
                total_loss += max_neg + math.log(exp_neg + math.exp(pos_sim - max_neg)) - pos_sim
            return OmniResult(data={"label_loss": total_loss / max(n, 1), "n_samples": n})
        except Exception as e:
            return OmniResult(error=Exception(f"Label CL failed: {e}"))

    def dual_loss(self, embeddings: List[List[float]], labels: List[int], alpha: float = 0.5) -> OmniResult:
        try:
            inst = self.instance_contrastive_loss(embeddings, labels)
            lbl = self.label_contrastive_loss(embeddings, labels)
            if not inst.is_ok() or not lbl.is_ok():
                return OmniResult(error=Exception("Sub-loss failed"))
            combined = alpha * inst.data["instance_loss"] + (1 - alpha) * lbl.data["label_loss"]
            return OmniResult(data={"dual_loss": combined, "instance_loss": inst.data["instance_loss"], "label_loss": lbl.data["label_loss"]})
        except Exception as e:
            return OmniResult(error=Exception(f"Dual CL failed: {e}"))
