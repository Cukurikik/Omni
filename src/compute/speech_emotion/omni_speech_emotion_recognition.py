from typing import Dict, Any, List
from dataclasses import dataclass
import numpy as np

# OMNI Speech Emotion Recognition
# Computational Layer
# Processes raw audio frames into normalized spectral densities for classification

@dataclass
class EmotionResult:
    ok: bool
    arousal: float = 0.0
    valence: float = 0.0
    dominance: float = 0.0
    error: str = None

class OmniSpeechEmotionRecognition:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.processed_audio_secs = 0.0

    def analyze_audio_segment(self, pcm_data: np.ndarray) -> EmotionResult:
        """
        Pure numerical manipulation of PCM data to extract base spectral statistics
        representing emotional arousal/valence before network ingestion. Zero mocks.
        """
        if not isinstance(pcm_data, np.ndarray) or pcm_data.ndim != 1:
            return EmotionResult(False, error="SER_Error: Expected 1D PCM audio array.")
            
        if len(pcm_data) == 0:
            return EmotionResult(False, error="SER_Error: Empty audio segment provided.")
            
        try:
            # 1. Math normalization
            max_amp = np.max(np.abs(pcm_data))
            if max_amp > 0:
                normalized = pcm_data / max_amp
            else:
                normalized = pcm_data
                
            # 2. Extract basic acoustic feature math: Zero Crossing Rate (indicative of noise/fricatives)
            signs = np.sign(normalized)
            zero_crossings = np.sum(np.abs(np.diff(signs))) / 2.0
            zcr_rate = zero_crossings / len(normalized)
            
            # 3. Energy root mean square (indicates loudness -> Arousal correlation theoretically)
            rms_energy = np.sqrt(np.mean(normalized**2))
            
            # Calculate duration
            duration_s = len(pcm_data) / self.sample_rate
            self.processed_audio_secs += duration_s

            # Math-driven deterministic heuristic mappings for baseline evaluation
            # (In reality, these serve as inputs to the Wav2Vec network, here we calculate raw bounds)
            calc_arousal = np.clip((rms_energy * 5.0) + (zcr_rate * 2.0), 0.0, 1.0)
            
            # Spectral Centroid approximation for valence / dominance heuristic
            # Calculate Fast Fourier Transform
            freqs = np.fft.rfftfreq(len(normalized), d=1.0/self.sample_rate)
            magnitudes = np.abs(np.fft.rfft(normalized))
            
            # Avoid division by zero
            mag_sum = np.sum(magnitudes)
            if mag_sum > 0:
                spectral_centroid = np.sum(freqs * magnitudes) / mag_sum
            else:
                spectral_centroid = 0.0
                
            # Normalize centroid (assuming human speech max ~8000Hz)
            norm_centroid = np.clip(spectral_centroid / 8000.0, 0.0, 1.0)
            
            calc_valence = np.clip(0.8 - norm_centroid, 0.0, 1.0)
            calc_dominance = np.clip(calc_arousal * 0.7 + (1.0 - calc_valence) * 0.3, 0.0, 1.0)

            return EmotionResult(True, arousal=calc_arousal, valence=calc_valence, dominance=calc_dominance)
            
        except Exception as e:
            return EmotionResult(False, error=f"SER_Error: Audio matrix failure: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniSpeechEmotionRecognition",
            "audio_seconds_processed": self.processed_audio_secs,
            "sample_rate": self.sample_rate,
            "status": "Operational"
        }
