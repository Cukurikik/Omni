"""
@omni-layer Compute | @omni-source eole-nlp/eole
@omni-description Open language modeling toolkit: encoder-decoder, decoder-only, and
encoder-only architectures with dynamic attention patterns.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniEoleLMToolkit:
    """Unified LM toolkit supporting enc-dec, dec-only, enc-only architectures."""
    ARCH_ENCODER_DECODER = "encoder_decoder"
    ARCH_DECODER_ONLY = "decoder_only"
    ARCH_ENCODER_ONLY = "encoder_only"

    def __init__(self, d_model: int = 512, n_heads: int = 8, n_layers: int = 6, architecture: str = "decoder_only"):
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.architecture = architecture

    def _causal_mask(self, seq_len: int) -> List[List[bool]]:
        return [[j <= i for j in range(seq_len)] for i in range(seq_len)]

    def _bidirectional_mask(self, seq_len: int) -> List[List[bool]]:
        return [[True]*seq_len for _ in range(seq_len)]

    def _attention_step(self, queries: List[List[float]], keys: List[List[float]], values: List[List[float]], mask: List[List[bool]]) -> List[List[float]]:
        d = len(queries[0]) if queries else 1
        scale = math.sqrt(d)
        output = []
        for i, q in enumerate(queries):
            scores = []
            for j, k in enumerate(keys):
                if mask[i][j]:
                    s = sum(q[dd]*k[dd] for dd in range(min(d, len(k)))) / scale
                else:
                    s = -1e9
                scores.append(s)
            max_s = max(scores) if scores else 0
            exp_s = [math.exp(s - max_s) for s in scores]
            total = sum(exp_s) + 1e-8
            weights = [e / total for e in exp_s]
            out = [sum(weights[t]*values[t][dd] for t in range(len(values))) for dd in range(d)]
            output.append(out)
        return output

    def forward(self, token_ids: List[int], encoder_ids: Optional[List[int]] = None) -> OmniResult:
        try:
            if not token_ids:
                return OmniResult(error=Exception("Empty input"))
            embeddings = [[math.sin((tid+1)*(d+1)*0.01)*0.02 for d in range(self.d_model)] for tid in token_ids]
            seq_len = len(token_ids)
            if self.architecture == self.ARCH_DECODER_ONLY:
                mask = self._causal_mask(seq_len)
            else:
                mask = self._bidirectional_mask(seq_len)
            hidden = embeddings
            for layer in range(self.n_layers):
                hidden = self._attention_step(hidden, hidden, hidden, mask)
                hidden = [[h[d] + math.tanh(h[d]*0.1) * 0.01 for d in range(self.d_model)] for h in hidden]
            if self.architecture == self.ARCH_ENCODER_DECODER and encoder_ids:
                enc_emb = [[math.sin((tid+1)*(d+1)*0.01)*0.02 for d in range(self.d_model)] for tid in encoder_ids]
                cross_mask = [[True]*len(encoder_ids) for _ in range(seq_len)]
                hidden = self._attention_step(hidden, enc_emb, enc_emb, cross_mask)
            return OmniResult(data={"architecture": self.architecture, "n_layers": self.n_layers, "output_shape": [len(hidden), self.d_model]})
        except Exception as e:
            return OmniResult(error=Exception(f"Eole forward failed: {e}"))
