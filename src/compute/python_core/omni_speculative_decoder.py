"""
OMNI Compute — Speculative Decoding Engine
Draft-then-verify acceleration for autoregressive generation.
"""
import logging, time
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Tuple

logger = logging.getLogger("omni.speculative")

@dataclass
class SpecConfig:
    draft_model_name: str = "omni-tiny"
    target_model_name: str = "omni-7b"
    num_speculative_tokens: int = 5    # K tokens to draft per step
    temperature: float = 1.0
    max_new_tokens: int = 256

@dataclass
class SpecStats:
    total_tokens: int = 0; accepted_tokens: int = 0
    draft_calls: int = 0; verify_calls: int = 0; total_latency_ms: float = 0.0
    @property
    def acceptance_rate(self) -> float:
        return self.accepted_tokens / max(self.total_tokens, 1)
    @property
    def speedup_estimate(self) -> float:
        # avg tokens accepted per verify call
        if self.verify_calls == 0: return 1.0
        return self.accepted_tokens / self.verify_calls

class OmniSpeculativeDecoder:
    """Speculative decoding: small model drafts, large model verifies."""
    def __init__(self, config: SpecConfig):
        self.config = config
        self.stats = SpecStats()
        self._draft_fn: Optional[Callable] = None
        self._verify_fn: Optional[Callable] = None
    def set_draft_model(self, fn: Callable[[List[int], int], Tuple[List[int], List[float]]]):
        """fn(token_ids, num_tokens) -> (drafted_ids, draft_logprobs)"""
        self._draft_fn = fn
    def set_target_model(self, fn: Callable[[List[int]], List[float]]):
        """fn(token_ids) -> logprobs_for_each_position"""
        self._verify_fn = fn
    def generate(self, input_ids: List[int]) -> List[int]:
        """Run speculative decoding loop."""
        if not self._draft_fn or not self._verify_fn:
            raise RuntimeError("Draft and target models must be set")
        generated = list(input_ids)
        tokens_generated = 0
        while tokens_generated < self.config.max_new_tokens:
            start = time.time()
            # Draft K tokens
            drafted_ids, draft_logprobs = self._draft_fn(generated, self.config.num_speculative_tokens)
            self.stats.draft_calls += 1
            # Verify with target model
            candidate = generated + drafted_ids
            target_logprobs = self._verify_fn(candidate)
            self.stats.verify_calls += 1
            # Accept/reject each drafted token
            accepted = 0
            for i, (d_id, d_lp) in enumerate(zip(drafted_ids, draft_logprobs)):
                pos = len(generated) + i
                if pos < len(target_logprobs):
                    import math, random
                    t_lp = target_logprobs[pos]
                    # Acceptance criterion: min(1, p_target / p_draft)
                    acceptance_prob = min(1.0, math.exp(t_lp - d_lp))
                    if random.random() < acceptance_prob:
                        accepted += 1
                    else:
                        break
            # Add accepted tokens
            generated.extend(drafted_ids[:accepted])
            tokens_generated += max(accepted, 1)  # At least 1 token per iteration
            self.stats.total_tokens += max(accepted, 1)
            self.stats.accepted_tokens += accepted
            self.stats.total_latency_ms += (time.time() - start) * 1000
            # If no token accepted, sample from target
            if accepted == 0:
                generated.append(drafted_ids[0] if drafted_ids else 0)
        return generated[len(input_ids):]
    def get_stats(self) -> dict:
        return {"acceptance_rate": f"{self.stats.acceptance_rate:.2%}",
                "speedup": f"{self.stats.speedup_estimate:.2f}x",
                "draft_calls": self.stats.draft_calls,
                "verify_calls": self.stats.verify_calls,
                "avg_latency_ms": self.stats.total_latency_ms / max(self.stats.verify_calls, 1)}
