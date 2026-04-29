from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI SHIELD Engine — Compute Layer
# Absorbing hukcc/SHIELD (ICLR 2026): Suppressing Hallucinations in LVLM Encoders.
# Implements bias detection and vulnerability scoring on visual encoder attention maps.

@dataclass
class ShieldResult:
    ok: bool
    hallucination_score: float = 0.0
    corrected_attention: np.ndarray = None
    error: str = None

class OmniShieldEngine:
    def __init__(self, vulnerability_threshold: float = 0.7):
        self.threshold = vulnerability_threshold
        self.evaluations = 0

    def detect_and_correct(self, attention_map: np.ndarray, visual_tokens: np.ndarray) -> ShieldResult:
        """
        Detects hallucination-prone attention patterns and applies correction.
        attention_map: (num_heads, seq_len, seq_len) — self-attention from vision encoder
        visual_tokens: (seq_len, hidden_dim) — token representations
        """
        if attention_map.ndim != 3:
            return ShieldResult(False, error="ShieldError: Expected 3D attention (heads, seq, seq)")
        if visual_tokens.ndim != 2:
            return ShieldResult(False, error="ShieldError: Expected 2D visual tokens (seq, dim)")
        try:
            self.evaluations += 1
            num_heads, seq_len, _ = attention_map.shape

            # Step 1: Compute per-head entropy (low entropy = high bias = hallucination risk)
            head_entropies = []
            for h in range(num_heads):
                attn = attention_map[h]
                attn_clipped = np.clip(attn, 1e-10, 1.0)
                entropy = -np.sum(attn_clipped * np.log(attn_clipped), axis=-1)
                head_entropies.append(np.mean(entropy))

            head_entropies = np.array(head_entropies)
            max_entropy = np.log(seq_len)
            normalized_entropy = head_entropies / max(max_entropy, 1e-10)

            # Step 2: Identify vulnerable heads (low normalized entropy)
            vulnerable_mask = normalized_entropy < (1.0 - self.threshold)
            hallucination_score = float(np.mean(vulnerable_mask))

            # Step 3: Correct by softening vulnerable head attention toward uniform
            corrected = attention_map.copy()
            uniform = np.ones((seq_len, seq_len)) / seq_len
            for h in range(num_heads):
                if vulnerable_mask[h]:
                    corrected[h] = 0.5 * corrected[h] + 0.5 * uniform

            return ShieldResult(True, hallucination_score=hallucination_score, corrected_attention=corrected)
        except Exception as e:
            return ShieldResult(False, error=f"ShieldError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniShieldEngine", "evaluations": self.evaluations,
                "threshold": self.threshold, "status": "Operational"}
