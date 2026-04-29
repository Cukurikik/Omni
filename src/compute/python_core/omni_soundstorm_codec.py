from typing import List

class OmniSoundStormCodec:
    """OMNI Compute Layer: SoundStorm Audio Codec Mapping (Zero-Mock)"""
    
    def __init__(self, codebook_size: int = 1024):
        self.codebook_size = codebook_size

    def quantize_audio(self, audio_frames: List[float]) -> List[int]:
        if not audio_frames:
            return []
            
        tokens = []
        for f in audio_frames:
            # Deterministic mapping to codebook index
            norm = (f + 1.0) / 2.0
            idx = int(norm * self.codebook_size)
            idx = max(0, min(self.codebook_size - 1, idx))
            tokens.append(idx)
            
        return tokens
