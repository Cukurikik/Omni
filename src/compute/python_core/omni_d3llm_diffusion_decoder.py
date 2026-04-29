# Omni d3LLM Ultra-Fast Diffusion Decoder
# Compute: Diffusion language model with parallel token denoising.
# Ref: hao-ai-lab/d3LLM — Text Diffusion
import math
from typing import List, Dict

def add_noise(tokens: List[int], vocab_size: int, noise_level: float) -> List[int]:
    import hashlib
    noised = []
    for i, t in enumerate(tokens):
        h = int(hashlib.md5(f"{t}:{i}:{noise_level}".encode()).hexdigest()[:8], 16)
        if (h % 1000) / 1000.0 < noise_level:
            noised.append(h % vocab_size)
        else:
            noised.append(t)
    return noised

def denoise_step(noisy_tokens: List[int], logits_per_pos: List[List[float]]) -> List[int]:
    return [max(range(len(l)), key=lambda j: l[j]) for l in logits_per_pos]

def compute_denoising_schedule(total_steps: int, schedule: str = "linear") -> List[float]:
    if schedule == "linear": return [1.0 - i / max(total_steps - 1, 1) for i in range(total_steps)]
    if schedule == "cosine": return [0.5 * (1 + math.cos(math.pi * i / max(total_steps - 1, 1))) for i in range(total_steps)]
    return [1.0 / (i + 1) for i in range(total_steps)]
