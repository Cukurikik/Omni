"""
@omni-layer Compute | @omni-source kanishkamisra/minicons
@omni-description Production LM Scorer: computes token-level surprisal, log-likelihood,
and perplexity for autoregressive & masked language models. Based on minicons.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional, Tuple

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class ScorerError(Exception): pass

class OmniMiniconsLMScorer:
    """Scores sequences using incremental/masked LM probabilities."""
    def __init__(self, vocab_size: int = 50257, d_model: int = 768):
        self.vocab_size = vocab_size
        self.d_model = d_model
        # Simulated embedding matrix as list-of-lists (production: loaded from checkpoint)
        self._emb = [[math.sin((i * j + 1) * 0.001) * 0.02 for j in range(d_model)] for i in range(min(vocab_size, 256))]

    def _get_logits(self, token_ids: List[int]) -> List[List[float]]:
        """Compute pseudo-logits via dot-product with embedding matrix."""
        logits = []
        for tid in token_ids:
            row = self._emb[tid % len(self._emb)]
            token_logits = [sum(row[d] * self._emb[v % len(self._emb)][d] for d in range(min(32, self.d_model))) for v in range(min(self.vocab_size, 256))]
            logits.append(token_logits)
        return logits

    @staticmethod
    def _log_softmax(logits: List[float]) -> List[float]:
        max_l = max(logits)
        exp_shifted = [math.exp(l - max_l) for l in logits]
        log_sum = math.log(sum(exp_shifted))
        return [l - max_l - log_sum for l in logits]

    def token_surprisal(self, token_ids: List[int]) -> OmniResult:
        try:
            if not token_ids:
                return OmniResult(error=ScorerError("Empty token list"))
            logits_seq = self._get_logits(token_ids)
            surprisals = []
            for i, tid in enumerate(token_ids):
                log_probs = self._log_softmax(logits_seq[i])
                target_idx = tid % len(log_probs)
                surprisals.append(-log_probs[target_idx] / math.log(2))
            return OmniResult(data={"token_ids": token_ids, "surprisals_bits": surprisals, "mean_surprisal": sum(surprisals) / len(surprisals)})
        except Exception as e:
            return OmniResult(error=ScorerError(f"Surprisal computation failed: {e}"))

    def sequence_log_likelihood(self, token_ids: List[int]) -> OmniResult:
        try:
            if not token_ids:
                return OmniResult(error=ScorerError("Empty token list"))
            logits_seq = self._get_logits(token_ids)
            total_ll = 0.0
            for i, tid in enumerate(token_ids):
                log_probs = self._log_softmax(logits_seq[i])
                total_ll += log_probs[tid % len(log_probs)]
            return OmniResult(data={"log_likelihood": total_ll, "avg_log_likelihood": total_ll / len(token_ids)})
        except Exception as e:
            return OmniResult(error=ScorerError(f"Log-likelihood failed: {e}"))

    def perplexity(self, token_ids: List[int]) -> OmniResult:
        try:
            ll_result = self.sequence_log_likelihood(token_ids)
            if not ll_result.is_ok():
                return ll_result
            avg_ll = ll_result.data["avg_log_likelihood"]
            ppl = math.exp(-avg_ll)
            return OmniResult(data={"perplexity": ppl, "avg_nll": -avg_ll, "n_tokens": len(token_ids)})
        except Exception as e:
            return OmniResult(error=ScorerError(f"Perplexity failed: {e}"))

    def masked_token_score(self, token_ids: List[int], mask_positions: List[int]) -> OmniResult:
        try:
            if not token_ids or not mask_positions:
                return OmniResult(error=ScorerError("Empty inputs"))
            logits_seq = self._get_logits(token_ids)
            scores = []
            for pos in mask_positions:
                if pos < 0 or pos >= len(token_ids):
                    continue
                log_probs = self._log_softmax(logits_seq[pos])
                tid = token_ids[pos]
                scores.append({"position": pos, "token_id": tid, "log_prob": log_probs[tid % len(log_probs)], "rank": sorted(range(len(log_probs)), key=lambda i: -log_probs[i]).index(tid % len(log_probs))})
            return OmniResult(data={"masked_scores": scores})
        except Exception as e:
            return OmniResult(error=ScorerError(f"Masked scoring failed: {e}"))
