# Omni DAEDAL Diffusion LLM Engine
# Ref: Li-Jinsong/DAEDAL
import math
from typing import List

def variable_length_denoise_schedule(t: int, t_max: int, base_noise: float = 0.1) -> float:
    """Calculate noise level for variable-length diffusion denoising step."""
    if t_max <= 0: return 0.0
    # Cosine scheduling approach
    ratio = t / t_max
    noise = base_noise * 0.5 * (1 + math.cos(ratio * math.pi))
    return round(noise, 6)

def sequence_reconstruction_loss(pred_logits: List[float], target_logits: List[float]) -> float:
    """MSE loss for sequence token logits reconstruction."""
    if not pred_logits or len(pred_logits) != len(target_logits):
        return 0.0
        
    mse = sum((p - t)**2 for p, t in zip(pred_logits, target_logits)) / len(pred_logits)
    return round(mse, 6)

def daedal_diffusion_step(latent_sequence: List[float], t: int, t_max: int) -> dict:
    """Simulate a DAEDAL forward/backward diffusion step on a latent sequence."""
    noise_level = variable_length_denoise_schedule(t, t_max)
    # Apply synthetic noise scaling
    noised_sequence = [round(x * (1.0 - noise_level), 4) for x in latent_sequence]
    
    return {
        "step": t,
        "noise_level": noise_level,
        "sequence_norm": round(math.sqrt(sum(x*x for x in noised_sequence)), 4)
    }
