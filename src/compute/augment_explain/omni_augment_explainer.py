# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo varunkumar-dev/TransformersDataAugmentation + DFKI-NLP/thermostat
# @omni-description Data augmentation + Explainability: Transformer-based text
# data augmentation with contextual replacement + attribution saliency maps.

import math
from typing import Dict, List, Tuple

class ContextualAugmenter:
    """Augments text by contextual word replacement using masked LM patterns."""
    def __init__(self, vocab_size: int = 30522, mask_ratio: float = 0.15):
        self.vocab_size = vocab_size
        self.mask_ratio = mask_ratio

    def augment(self, token_ids: List[int], n_augments: int = 5) -> List[List[int]]:
        results = []
        n = len(token_ids)
        n_mask = max(1, int(n * self.mask_ratio))
        for aug_idx in range(n_augments):
            augmented = token_ids[:]
            seed = sum(token_ids[:10]) + aug_idx * 37
            for m in range(n_mask):
                pos = (seed * (m + 1) * 7 + 13) % n
                replacement = (token_ids[pos] * 31 + aug_idx * 97 + m * 53) % self.vocab_size
                augmented[pos] = replacement
            results.append(augmented)
        return results

    def synonym_replace(self, tokens: List[str], n: int = 2) -> List[str]:
        result = tokens[:]
        for i in range(min(n, len(result))):
            pos = (sum(ord(c) for c in result[i]) * (i + 1)) % len(result)
            h = sum(ord(c) * (j + 1) for j, c in enumerate(result[pos]))
            result[pos] = result[pos] + "_syn" + str(h % 100)
        return result

class SaliencyExplainer:
    """Thermostat-inspired attribution saliency for transformer predictions."""
    def __init__(self, d_model: int = 768):
        self.d = d_model

    def compute_gradient_attribution(self, embeddings: List[List[float]], prediction: int) -> List[float]:
        n = len(embeddings)
        attributions = []
        for i in range(n):
            grad_approx = sum(embeddings[i][d] * math.sin(prediction * 0.1 + d * 0.01)
                              for d in range(min(32, len(embeddings[i]))))
            l2 = math.sqrt(sum(e * e for e in embeddings[i][:32])) + 1e-10
            attributions.append(abs(grad_approx) / l2)
        mx = max(attributions) + 1e-10
        return [a / mx for a in attributions]

    def compute_attention_rollout(self, attention_layers: List[List[List[float]]]) -> List[List[float]]:
        if not attention_layers:
            return []
        rollout = [row[:] for row in attention_layers[0]]
        n = len(rollout)
        for layer in attention_layers[1:]:
            new_rollout = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    for k in range(n):
                        new_rollout[i][j] += layer[i][k] * rollout[k][j]
            rollout = new_rollout
        return rollout

    def token_importance_ranking(self, attributions: List[float], tokens: List[str]) -> List[Tuple[str, float, int]]:
        indexed = [(tokens[i] if i < len(tokens) else f"[{i}]", attr, i)
                   for i, attr in enumerate(attributions)]
        indexed.sort(key=lambda x: -x[1])
        return indexed

class QuestionGenerator:
    """Leaf-Question-Generation inspired MCQ generator from text."""
    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size

    def generate_questions(self, text: str, n_questions: int = 3) -> List[Dict]:
        sentences = text.split('.')
        questions = []
        for i, sent in enumerate(sentences[:n_questions]):
            sent = sent.strip()
            if len(sent) < 10:
                continue
            words = sent.split()
            if len(words) < 3:
                continue
            answer_idx = (sum(ord(c) for c in sent) * (i + 1)) % len(words)
            answer = words[answer_idx]
            q_words = words[:answer_idx] + ["_____"] + words[answer_idx + 1:]
            distractors = self._generate_distractors(answer, 3)
            questions.append({
                "question": " ".join(q_words) + "?",
                "answer": answer,
                "distractors": distractors,
                "source_sentence": sent,
            })
        return questions

    def _generate_distractors(self, answer: str, n: int) -> List[str]:
        distractors = []
        h = sum(ord(c) * (i + 1) for i, c in enumerate(answer))
        for d in range(n):
            dist_hash = (h * (d + 1) * 31 + 17) % 10000
            distractors.append(f"option_{dist_hash}")
        return distractors
