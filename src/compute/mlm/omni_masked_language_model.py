"""
@omni-layer Compute | @omni-source lucidrains/mlm-pytorch
@omni-description Masked Language Modeling engine: BERT-style masking strategy with
configurable mask/replace/random probabilities. Production-grade token corruption.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math, random
from typing import List, Optional, Tuple

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class MLMError(Exception): pass

class OmniMaskedLanguageModel:
    """Production MLM with configurable masking strategy."""
    def __init__(self, vocab_size: int = 30522, mask_prob: float = 0.15, replace_prob: float = 0.8, random_prob: float = 0.1, mask_token_id: int = 103, pad_token_id: int = 0, cls_token_id: int = 101, sep_token_id: int = 102):
        self.vocab_size = vocab_size
        self.mask_prob = mask_prob
        self.replace_prob = replace_prob
        self.random_prob = random_prob
        self.mask_token_id = mask_token_id
        self.pad_token_id = pad_token_id
        self.special_tokens = {pad_token_id, cls_token_id, sep_token_id}

    def create_masked_input(self, token_ids: List[int], seed: int = 42) -> OmniResult:
        try:
            if not token_ids:
                return OmniResult(error=MLMError("Empty token list"))
            rng = random.Random(seed)
            masked_ids = list(token_ids)
            labels = [self.pad_token_id] * len(token_ids)
            mask_positions = []
            for i, tid in enumerate(token_ids):
                if tid in self.special_tokens:
                    continue
                if rng.random() < self.mask_prob:
                    labels[i] = tid
                    mask_positions.append(i)
                    r = rng.random()
                    if r < self.replace_prob:
                        masked_ids[i] = self.mask_token_id
                    elif r < self.replace_prob + self.random_prob:
                        masked_ids[i] = rng.randint(0, self.vocab_size - 1)
            return OmniResult(data={"masked_input": masked_ids, "labels": labels, "mask_positions": mask_positions, "n_masked": len(mask_positions), "mask_ratio": len(mask_positions) / max(1, len(token_ids))})
        except Exception as e:
            return OmniResult(error=MLMError(f"Masking failed: {e}"))

    def compute_mlm_loss(self, logits: List[List[float]], labels: List[int]) -> OmniResult:
        try:
            if len(logits) != len(labels):
                return OmniResult(error=MLMError("Logits/labels length mismatch"))
            total_loss = 0.0
            n_valid = 0
            for i, label in enumerate(labels):
                if label == self.pad_token_id:
                    continue
                row = logits[i]
                max_l = max(row)
                exp_l = [math.exp(l - max_l) for l in row]
                log_sum = math.log(sum(exp_l))
                log_prob = row[label % len(row)] - max_l - log_sum
                total_loss -= log_prob
                n_valid += 1
            if n_valid == 0:
                return OmniResult(data={"loss": 0.0, "n_masked": 0})
            return OmniResult(data={"loss": total_loss / n_valid, "n_masked": n_valid, "total_nll": total_loss})
        except Exception as e:
            return OmniResult(error=MLMError(f"Loss computation failed: {e}"))

    def whole_word_masking(self, token_ids: List[int], word_boundaries: List[Tuple[int,int]], seed: int = 42) -> OmniResult:
        try:
            if not token_ids or not word_boundaries:
                return OmniResult(error=MLMError("Empty inputs"))
            rng = random.Random(seed)
            masked_ids = list(token_ids)
            labels = [self.pad_token_id] * len(token_ids)
            masked_words = 0
            for start, end in word_boundaries:
                if rng.random() < self.mask_prob:
                    for pos in range(start, min(end, len(token_ids))):
                        labels[pos] = token_ids[pos]
                        masked_ids[pos] = self.mask_token_id
                    masked_words += 1
            return OmniResult(data={"masked_input": masked_ids, "labels": labels, "n_masked_words": masked_words})
        except Exception as e:
            return OmniResult(error=MLMError(f"WWM failed: {e}"))
