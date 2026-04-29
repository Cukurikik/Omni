import librosa
import numpy as np
from typing import Dict, Any
from omni_core.result import OmniResult, Ok, Err

class AudioFeatureExtractor:
    """
    OMNI COMPUTE LAYER: DL Music Analysis
    Computes Mel-spectrograms and MFCCs from raw audio arrays.
    Zero-Mock: Uses Librosa DSP math.
    """
    def __init__(self, sr: int = 22050, n_mels: int = 128, n_mfcc: int = 13):
        self.sr = sr
        self.n_mels = n_mels
        self.n_mfcc = n_mfcc

    def extract_features(self, y: np.ndarray) -> OmniResult[Dict[str, np.ndarray], str]:
        try:
            # Mel Spectrogram
            mel_spec = librosa.feature.melspectrogram(y=y, sr=self.sr, n_mels=self.n_mels)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # MFCC
            mfcc = librosa.feature.mfcc(S=mel_spec_db, n_mfcc=self.n_mfcc)
            
            # Chromagram
            chroma = librosa.feature.chroma_stft(y=y, sr=self.sr)

            return Ok({
                "mel_spectrogram": mel_spec_db,
                "mfcc": mfcc,
                "chroma": chroma
            })
        except Exception as e:
            return Err(f"Audio feature extraction failed: {str(e)}")
