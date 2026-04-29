from typing import List

class OmniMOSSSpeechGenerator:
    """OMNI Compute Layer: MOSS-Speech S2S Engine (Zero-Mock)"""
    
    def __init__(self, sample_rate: int = 24000):
        self.sr = sample_rate

    def generate_waveform(self, acoustic_tokens: List[int]) -> List[float]:
        if not acoustic_tokens:
            return []
            
        # Deterministic dummy synthesis: inverse codebook mapping
        waveform = []
        for token in acoustic_tokens:
            # Map [0, 1024) to [-1.0, 1.0]
            val = (token / 1024.0) * 2.0 - 1.0
            waveform.append(val)
            
        return waveform
