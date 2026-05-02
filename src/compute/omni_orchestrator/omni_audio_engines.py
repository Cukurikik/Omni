"""
@omni-domain Compute Layer (Audio Processing)
@omni-source various/audio-engines
@omni-description Omni Audio Engines mimicking audio processing pipelines.
@omni-requirement zero-mock, monadic-error
"""
import math
from typing import Any, Optional, List

class OmniResult:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error
    def is_ok(self): return self.error is None

class AudioError(Exception): pass

class OmniAudioEngines:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def apply_low_pass_filter(self, samples: List[float], cutoff_hz: float) -> OmniResult:
        try:
            if not samples:
                return OmniResult(error=AudioError("Samples empty."))
            if cutoff_hz <= 0:
                return OmniResult(error=AudioError("Cutoff must be positive."))
            rc = 1.0 / (2 * math.pi * cutoff_hz)
            dt = 1.0 / self.sample_rate
            alpha = dt / (rc + dt)
            filtered = [samples[0]]
            for i in range(1, len(samples)):
                filtered.append(filtered[-1] + alpha * (samples[i] - filtered[-1]))
            return OmniResult(data={"filtered": filtered, "cutoff_hz": cutoff_hz})
        except Exception as e:
            return OmniResult(error=AudioError(f"Filter failed: {e}"))

    def compute_rms(self, samples: List[float]) -> OmniResult:
        try:
            if not samples:
                return OmniResult(error=AudioError("Samples empty."))
            rms = math.sqrt(sum(s*s for s in samples) / len(samples))
            return OmniResult(data={"rms": rms, "db": 20 * math.log10(max(rms, 1e-10))})
        except Exception as e:
            return OmniResult(error=AudioError(f"RMS failed: {e}"))

    def normalize(self, samples: List[float], target_db: float = -3.0) -> OmniResult:
        try:
            if not samples:
                return OmniResult(error=AudioError("Samples empty."))
            peak = max(abs(s) for s in samples)
            if peak == 0:
                return OmniResult(data={"normalized": samples})
            target_amplitude = 10 ** (target_db / 20.0)
            gain = target_amplitude / peak
            normalized = [s * gain for s in samples]
            return OmniResult(data={"normalized": normalized, "gain_applied": gain})
        except Exception as e:
            return OmniResult(error=AudioError(f"Normalization failed: {e}"))
