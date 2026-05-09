"""
@omni-layer Compute | @omni-source sidharthrajaram/StyleTTS2
@omni-description StyleTTS2 engine: style diffusion for human-level TTS with
prosody modeling, duration prediction, and style vector transfer.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniStyleTTS:
    def __init__(self, d_style=256, d_text=512, n_mels=80, sample_rate=24000):
        self.d_style = d_style; self.d_text = d_text
        self.n_mels = n_mels; self.sample_rate = sample_rate
        self.diffusion_steps = 10

    def text_to_phoneme(self, text: str) -> List[str]:
        phoneme_map = {'a':'AH','e':'EH','i':'IH','o':'OW','u':'UH','s':'S','t':'T','n':'N','r':'R','l':'L'}
        return [phoneme_map.get(c.lower(), 'SP') for c in text if c.isalpha() or c == ' '][:200]

    def predict_durations(self, phonemes: List[str]) -> List[int]:
        durations = []
        for p in phonemes:
            base = 5 if p in ('SP',) else 8
            durations.append(base + len(p))
        return durations

    def extract_style_vector(self, reference_features: List[float]) -> List[float]:
        style = [0.0]*self.d_style
        for i in range(min(len(reference_features), self.d_style)):
            style[i] = math.tanh(reference_features[i] * 0.5)
        norm = math.sqrt(sum(v*v for v in style) + 1e-8)
        return [v/norm for v in style]

    def diffusion_sample(self, style: List[float], text_emb: List[float]) -> List[List[float]]:
        n_frames = len(text_emb) * 3
        mel = [[0.0]*self.n_mels for _ in range(n_frames)]
        for step in range(self.diffusion_steps):
            t = 1.0 - step / self.diffusion_steps
            for f in range(n_frames):
                for m in range(self.n_mels):
                    noise = math.sin((f+1)*(m+1)*0.01 + step) * t
                    style_influence = style[m % len(style)] * (1 - t)
                    mel[f][m] = mel[f][m] * 0.9 + style_influence + noise * 0.1
        return mel

    def synthesize(self, text: str, reference_audio_features: List[float] = None) -> OmniResult:
        try:
            phonemes = self.text_to_phoneme(text)
            durations = self.predict_durations(phonemes)
            total_frames = sum(durations)
            ref = reference_audio_features or [math.sin(i*0.1) for i in range(self.d_style)]
            style = self.extract_style_vector(ref)
            text_emb = [math.cos(i*0.05) for i in range(len(phonemes))]
            mel = self.diffusion_sample(style, text_emb)
            audio_len_sec = total_frames * 256 / self.sample_rate
            return OmniResult(data={
                "n_phonemes": len(phonemes), "n_mel_frames": len(mel),
                "duration_sec": audio_len_sec, "sample_rate": self.sample_rate,
                "mel_shape": [len(mel), self.n_mels],
                "style_norm": math.sqrt(sum(v*v for v in style))
            })
        except Exception as e: return OmniResult(error=e)
