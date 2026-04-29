# Omni Music Gen Latent Engine (Python)
# Compute Layer: Diffusion-based latent music representation.
# Ref: shaopengw/Awesome-Music-Generation

from typing import List
import math

def generate_sine_latent(freq: float, dur: float, sr: int = 44100) -> List[float]:
    if freq <= 0 or dur <= 0 or sr <= 0:
        return []
    n = int(dur * sr)
    return [round(math.sin(2*math.pi*freq*t/sr), 8) for t in range(n)]

def mel_to_hz(mel: float) -> float:
    return 700.0 * (10.0**(mel/2595.0) - 1.0)

def spectral_centroid(mags: List[float], freqs: List[float]) -> float:
    if len(mags) != len(freqs) or not mags:
        return 0.0
    ws = sum(m*f for m,f in zip(mags, freqs))
    tm = sum(mags)
    return round(ws/tm, 6) if tm > 0 else 0.0
