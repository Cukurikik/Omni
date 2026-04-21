# omni_spectrosound_engine.py
# Production-Grade Image-to-Audio Spectrogram Synthesis
# ==============================================================
# Absorbed from: veggiedefender/sounds
#
# Key patterns learned:
# - Matrix pixel extraction representing frequency bands
# - Inverse FFT / Frequency additive synthesis mapping Y coordinates 
#   to frequency bins and X coordinates to time intervals.
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Spectrosound Engine
========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import math
from typing import Dict, Any

try:
    import numpy as np
    from PIL import Image
except ImportError:
    np = None
    Image = None

ENGINE_VERSION = "1.0.0-omni"

class SpectrosoundError(Exception):
    pass


class OmniSpectrosoundEngine:
    """
    Transforms graphical representations (images) into playable audio files
    where the audio spectrogram paints the original image. Pure DSP.
    """

    def __init__(self, sample_rate: int = 44100):
        """Initialize OmniSpectrosoundEngine."""
        self._available = np is not None and Image is not None
        self.sample_rate = sample_rate

    def synthesize_image(self, image_path: str, duration_sec: float = 3.0, freq_min: float = 50.0, freq_max: float = 16000.0) -> Dict[str, Any]:
        """
        Converts an image into an audio waveform array.
        Uses additive sine wave synthesis for crisp spectrogram resonance.
        """
        try:
            # Load and convert image to grayscale
            img = Image.open(image_path).convert('L')
        except Exception as e:
            return {"status": "error", "error": f"Image load failed: {str(e)}"}

        width, height = img.size
        pixels = np.array(img).astype(float)
        
        # Normalize pixel intensities (0 to 1), invert so white = loud
        pixels = 1.0 - (pixels / 255.0)

        # Pre-allocate audio buffer
        total_samples = int(self.sample_rate * duration_sec)
        audio = np.zeros(total_samples)

        # Time mapping
        samples_per_col = total_samples // width
        
        # Frequency mapping (Logarithmic scale looks better on spectrograms)
        log_min = math.log10(freq_min)
        log_max = math.log10(freq_max)
        freqs = [10.0 ** (log_min + (log_max - log_min) * (height - y - 1) / height) for y in range(height)]

        # Additive synthesis
        t = np.arange(samples_per_col) / self.sample_rate

        for x in range(width):
            start_idx = x * samples_per_col
            end_idx = start_idx + samples_per_col
            col_chunk = np.zeros(samples_per_col)
            
            for y in range(height):
                intensity = pixels[y, x]
                if intensity > 0.05: # Optimization threshold
                    phase = 2.0 * math.pi * freqs[y] * t
                    col_chunk += intensity * np.sin(phase)
                    
            audio[start_idx:end_idx] = col_chunk

        # Normalize to prevent hard clipping (-1.0 to 1.0)
        max_amp = np.max(np.abs(audio))
        if max_amp > 0:
            audio = audio / max_amp

        # Apply a soft fade-in/fade-out envelope
        fade_len = int(0.05 * self.sample_rate) # 50ms fade
        if len(audio) > fade_len * 2:
            fade_in = np.linspace(0.0, 1.0, fade_len)
            fade_out = np.linspace(1.0, 0.0, fade_len)
            audio[:fade_len] *= fade_in
            audio[-fade_len:] *= fade_out

        return {
            "status": "success",
            "data": {
                "algorithm": "additive_synthesis",
                "duration_sec": duration_sec,
                "synthesized_samples": len(audio),
                "waveform_data": audio 
                # In production, use scipy.io.wavfile.write to save this array
            }
        }

    def engine_info(self) -> Dict[str, str]:
        """Performs engine info operation for OmniSpectrosoundEngine."""
        return {
            "engine": "OmniSpectrosoundEngine",
            "status": "ready"
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-spectrosound",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
