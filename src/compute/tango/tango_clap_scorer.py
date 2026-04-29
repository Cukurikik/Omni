# Tango CLAP-Ranked Preference Optimization
# Cosine similarity scoring for audio-text alignment

import torch
from typing import Optional, Generic, TypeVar, List
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class CLAPScorer:
    MAX_DIM = 1024
    MAX_CANDIDATES = 256

    def score_candidates(self, text_emb: torch.Tensor, audio_embs: List[torch.Tensor]) -> OmniResult[List[float], str]:
        if text_emb.shape[-1] > self.MAX_DIM:
            return OmniResult(error=f"Embedding dim exceeds {self.MAX_DIM}")
        if len(audio_embs) > self.MAX_CANDIDATES:
            return OmniResult(error=f"Candidates exceed {self.MAX_CANDIDATES}")
        scores = []
        text_norm = torch.nn.functional.normalize(text_emb.unsqueeze(0), dim=-1)
        for audio_emb in audio_embs:
            if audio_emb.shape != text_emb.shape:
                return OmniResult(error="Dimension mismatch between text and audio embeddings")
            audio_norm = torch.nn.functional.normalize(audio_emb.unsqueeze(0), dim=-1)
            cos_sim = torch.mm(text_norm, audio_norm.t()).item()
            scores.append(cos_sim)
        return OmniResult(value=scores)

    def rank_by_preference(self, scores: List[float]) -> OmniResult[List[int], str]:
        if not scores:
            return OmniResult(error="Empty score list")
        indexed = list(enumerate(scores))
        indexed.sort(key=lambda x: x[1], reverse=True)
        return OmniResult(value=[idx for idx, _ in indexed])
