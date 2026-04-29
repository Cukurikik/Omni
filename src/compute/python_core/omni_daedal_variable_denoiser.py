# Omni DAEDAL Variable-Length Denoiser (Python)
# Compute Layer: Training-free variable-length denoising for diffusion LLMs.
# Ref: Li-Jinsong/DAEDAL — ICLR 2026, Beyond Fixed Denoising.

import math
from typing import List, Tuple

def compute_noise_schedule(timesteps: int, beta_start: float = 0.0001, beta_end: float = 0.02) -> List[float]:
    if timesteps <= 0:
        return []
    return [beta_start + (beta_end - beta_start) * (t / max(timesteps - 1, 1)) for t in range(timesteps)]

def variable_length_denoise(
    noisy_logits: List[float],
    target_length: int,
    noise_scale: float = 1.0
) -> List[float]:
    if target_length <= 0 or not noisy_logits:
        return []
    src_len = len(noisy_logits)
    ratio = src_len / target_length
    denoised: List[float] = []
    for i in range(target_length):
        src_idx = min(int(i * ratio), src_len - 1)
        val = noisy_logits[src_idx]
        correction = noise_scale * math.exp(-abs(val) * 0.5)
        denoised.append(round(val - correction, 8))
    return denoised

def adaptive_timestep_selector(token_count: int, base_steps: int = 50) -> int:
    if token_count <= 0:
        return base_steps
    return max(1, int(base_steps * math.log2(max(token_count, 2))))
