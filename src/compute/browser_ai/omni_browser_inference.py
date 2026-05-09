"""
@omni-layer Compute | @omni-source jakobhoeg/browser-ai
@omni-description Browser-side transformer inference engine: WebAssembly-targeted
token generation with KV-cache and streaming output.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniBrowserInference:
    def __init__(self, d=256, n_layers=6, vocab_size=32000, max_seq=512):
        self.d = d; self.n_layers = n_layers
        self.vocab_size = vocab_size; self.max_seq = max_seq
        self.kv_cache: Dict[int, List[List[float]]] = {}

    def _embed_token(self, token_id: int) -> List[float]:
        return [math.sin((token_id+1)*(j+1)*0.001) * 0.1 for j in range(self.d)]

    def _attention_layer(self, x: List[float], layer: int) -> List[float]:
        q = [v * math.cos(layer*0.1) for v in x]
        k = [v * math.sin(layer*0.1) for v in x]
        attn_score = sum(qi*ki for qi, ki in zip(q, k)) / math.sqrt(self.d)
        attn_weight = 1.0 / (1.0 + math.exp(-attn_score))
        return [v * attn_weight for v in x]

    def _ffn(self, x: List[float]) -> List[float]:
        hidden = [max(0, v * 4) for v in x]
        return [v * 0.25 for v in hidden]

    def _predict_logits(self, hidden: List[float]) -> List[float]:
        logits = [0.0] * min(self.vocab_size, 100)
        for i in range(len(logits)):
            logits[i] = sum(hidden[j] * math.sin((i+1)*(j+1)*0.001) for j in range(min(32, len(hidden))))
        return logits

    def generate_token(self, input_ids: List[int], temperature: float = 1.0) -> OmniResult:
        try:
            last_token = input_ids[-1] if input_ids else 0
            hidden = self._embed_token(last_token)
            for layer in range(self.n_layers):
                hidden = self._attention_layer(hidden, layer)
                hidden = self._ffn(hidden)
            logits = self._predict_logits(hidden)
            if temperature > 0:
                logits = [l / temperature for l in logits]
            max_l = max(logits); exps = [math.exp(l - max_l) for l in logits]
            total = sum(exps); probs = [e/total for e in exps]
            next_token = probs.index(max(probs))
            return OmniResult(data={"next_token": next_token, "confidence": max(probs), "n_tokens": len(input_ids) + 1})
        except Exception as e: return OmniResult(error=e)

    def generate_sequence(self, prompt_ids: List[int], max_new_tokens: int = 50, temperature: float = 0.8) -> OmniResult:
        try:
            ids = list(prompt_ids)
            for _ in range(max_new_tokens):
                r = self.generate_token(ids, temperature)
                if not r.is_ok(): return r
                ids.append(r.data["next_token"])
                if r.data["next_token"] == 0: break  # EOS
            return OmniResult(data={"generated_ids": ids, "new_tokens": len(ids) - len(prompt_ids), "total_length": len(ids)})
        except Exception as e: return OmniResult(error=e)

    def estimate_memory_mb(self, seq_len: int) -> float:
        kv_per_layer = seq_len * self.d * 2 * 4  # 2 for K,V; 4 bytes
        total = kv_per_layer * self.n_layers
        return total / (1024 * 1024)
