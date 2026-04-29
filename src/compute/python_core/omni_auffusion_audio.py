# Omni Auffusion Text-to-Audio Engine
# Ref: happylittlecat2333/Auffusion — Diffusion + LLM for audio generation
import math
from typing import List, Dict

def mel_spectrogram_energy(mel_bands: List[List[float]]) -> Dict:
    total = sum(sum(b) for b in mel_bands)
    n_frames = len(mel_bands)
    n_bands = len(mel_bands[0]) if mel_bands else 0
    return {"total_energy": round(total, 4), "avg_per_frame": round(total / max(n_frames, 1), 4),
            "n_frames": n_frames, "n_bands": n_bands}

def frechet_audio_distance(mu1: List[float], mu2: List[float], sigma1: List[float], sigma2: List[float]) -> float:
    d = len(mu1)
    mean_diff_sq = sum((m1 - m2)**2 for m1, m2 in zip(mu1, mu2))
    trace_sum = sum(s1 + s2 - 2 * math.sqrt(max(s1 * s2, 0)) for s1, s2 in zip(sigma1, sigma2))
    return round(mean_diff_sq + trace_sum, 4)

def audio_caption_similarity(caption_embedding: List[float], audio_embedding: List[float]) -> float:
    dot = sum(c * a for c, a in zip(caption_embedding, audio_embedding))
    norm_c = math.sqrt(sum(c**2 for c in caption_embedding)) or 1
    norm_a = math.sqrt(sum(a**2 for a in audio_embedding)) or 1
    return round(dot / (norm_c * norm_a), 4)
