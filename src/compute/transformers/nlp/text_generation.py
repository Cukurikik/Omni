"""
OMNI Transformer — Text Generation Pipeline
Production text generation with beam search, sampling, repetition penalty.
Learned from: pszemraj/ai-msgbot, LowinLi/fastgpt
"""
import torch
import torch.nn.functional as F
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    max_new_tokens: int = 256
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.9
    repetition_penalty: float = 1.2
    num_beams: int = 1
    do_sample: bool = True
    eos_token_id: Optional[int] = None
    pad_token_id: int = 0
    length_penalty: float = 1.0
    no_repeat_ngram_size: int = 3


class TextGenerator:
    """Production text generation with advanced decoding strategies."""
    def __init__(self, model, tokenizer, config: GenerationConfig = None):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config or GenerationConfig()
        self.device = next(model.parameters()).device

    def _apply_repetition_penalty(self, logits: torch.Tensor, generated: torch.Tensor) -> torch.Tensor:
        if self.config.repetition_penalty == 1.0:
            return logits
        for token_id in generated[0].tolist():
            if logits[0, token_id] < 0:
                logits[0, token_id] *= self.config.repetition_penalty
            else:
                logits[0, token_id] /= self.config.repetition_penalty
        return logits

    def _apply_no_repeat_ngram(self, logits: torch.Tensor, generated: torch.Tensor) -> torch.Tensor:
        n = self.config.no_repeat_ngram_size
        if n <= 0 or generated.size(1) < n:
            return logits
        gen_list = generated[0].tolist()
        ngrams = set()
        for i in range(len(gen_list) - n + 1):
            ngrams.add(tuple(gen_list[i:i + n]))
        if len(gen_list) >= n - 1:
            prefix = tuple(gen_list[-(n - 1):])
            for ngram in ngrams:
                if ngram[:-1] == prefix:
                    logits[0, ngram[-1]] = float("-inf")
        return logits

    @torch.inference_mode()
    def generate(self, prompt: str, **kwargs) -> str:
        config = GenerationConfig(**{**vars(self.config), **kwargs})
        encoded = self.tokenizer.encode(prompt)
        input_ids = torch.tensor([encoded["input_ids"]], device=self.device)

        if config.num_beams > 1:
            return self._beam_search(input_ids, config)
        return self._sample(input_ids, config)

    def _sample(self, input_ids: torch.Tensor, config: GenerationConfig) -> str:
        generated = input_ids
        kv_caches = None

        for _ in range(config.max_new_tokens):
            inp = generated if kv_caches is None else generated[:, -1:]
            outputs = self.model(inp, use_cache=True, kv_caches=kv_caches) if hasattr(self.model, 'forward') else self.model(inp)
            if isinstance(outputs, dict):
                kv_caches = outputs.get("kv_caches")
                logits = outputs["logits"][:, -1, :]
            else:
                logits = outputs[:, -1, :]

            logits = self._apply_repetition_penalty(logits, generated)
            logits = self._apply_no_repeat_ngram(logits, generated)
            logits = logits / max(config.temperature, 1e-6)

            if config.top_k > 0:
                v, _ = torch.topk(logits, min(config.top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")

            if config.top_p < 1.0:
                sorted_logits, sorted_idx = torch.sort(logits, descending=True)
                cumsum = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                remove = cumsum - F.softmax(sorted_logits, dim=-1) > config.top_p
                sorted_logits[remove] = float("-inf")
                logits.scatter_(1, sorted_idx, sorted_logits)

            probs = F.softmax(logits, dim=-1)
            if config.do_sample:
                next_token = torch.multinomial(probs, 1)
            else:
                next_token = logits.argmax(dim=-1, keepdim=True)

            generated = torch.cat([generated, next_token], dim=1)
            if config.eos_token_id is not None and next_token.item() == config.eos_token_id:
                break

        new_tokens = generated[0, input_ids.size(1):].tolist()
        return self.tokenizer.decode(new_tokens)

    def _beam_search(self, input_ids: torch.Tensor, config: GenerationConfig) -> str:
        beams = [(input_ids, 0.0)]  # (sequence, log_prob)

        for step in range(config.max_new_tokens):
            candidates = []
            for seq, score in beams:
                outputs = self.model(seq)
                logits = outputs["logits"][:, -1, :] if isinstance(outputs, dict) else outputs[:, -1, :]
                log_probs = F.log_softmax(logits, dim=-1)
                topk_log_probs, topk_ids = torch.topk(log_probs, config.num_beams)

                for k in range(config.num_beams):
                    new_seq = torch.cat([seq, topk_ids[:, k:k+1]], dim=1)
                    new_score = score + topk_log_probs[0, k].item()
                    length_factor = ((5 + new_seq.size(1)) / 6) ** config.length_penalty
                    candidates.append((new_seq, new_score / length_factor))

            beams = sorted(candidates, key=lambda x: x[1], reverse=True)[:config.num_beams]

            if config.eos_token_id is not None:
                if all(b[0][0, -1].item() == config.eos_token_id for b in beams):
                    break

        best_seq = beams[0][0]
        return self.tokenizer.decode(best_seq[0, input_ids.size(1):].tolist())
