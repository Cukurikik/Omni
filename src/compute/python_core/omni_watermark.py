"""OMNI Compute — Watermark Detection for AI-Generated Text"""
import hashlib, math; from typing import List, Tuple, Dict

class OmniWatermarker:
    """Embed and detect invisible watermarks in LLM-generated text."""
    def __init__(self, vocab_size: int = 32000, gamma: float = 0.5, delta: float = 2.0, key: str = "omni-secret"):
        self.vocab_size = vocab_size; self.gamma = gamma; self.delta = delta; self.key = key
    def _get_greenlist(self, prev_token: int) -> set:
        h = hashlib.sha256(f"{self.key}:{prev_token}".encode()).digest()
        rng_seed = int.from_bytes(h[:4], "big")
        import random; rng = random.Random(rng_seed)
        all_ids = list(range(self.vocab_size))
        rng.shuffle(all_ids)
        green_size = int(self.vocab_size * self.gamma)
        return set(all_ids[:green_size])
    def apply_watermark(self, logits: List[float], prev_token: int) -> List[float]:
        greenlist = self._get_greenlist(prev_token)
        return [l + self.delta if i in greenlist else l for i, l in enumerate(logits)]
    def detect(self, token_ids: List[int]) -> Dict:
        if len(token_ids) < 2: return {"is_watermarked": False, "confidence": 0.0}
        green_count = 0
        for i in range(1, len(token_ids)):
            greenlist = self._get_greenlist(token_ids[i-1])
            if token_ids[i] in greenlist: green_count += 1
        total = len(token_ids) - 1
        green_fraction = green_count / max(total, 1)
        expected = self.gamma
        z_score = (green_fraction - expected) / max(math.sqrt(expected * (1-expected) / total), 1e-8)
        return {"is_watermarked": z_score > 4.0, "z_score": round(z_score, 2),
                "green_fraction": round(green_fraction, 4), "expected": expected,
                "green_count": green_count, "total_tokens": total}
