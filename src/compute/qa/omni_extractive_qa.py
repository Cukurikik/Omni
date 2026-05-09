"""
@omni-layer Compute | @omni-source savasy/Turkish-Bert-NLP-Pipeline
@omni-description Question Answering engine with extractive span prediction:
start/end logit computation with sliding window for long documents.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniExtractiveQA:
    def __init__(self, d=768, max_answer_len=30):
        self.d = d; self.max_answer_len = max_answer_len
        self.start_weights = [math.sin((j+1)*0.005)*0.02 for j in range(d)]
        self.end_weights = [math.cos((j+1)*0.005)*0.02 for j in range(d)]

    def predict_span(self, token_embeddings: List[List[float]], question_len: int) -> OmniResult:
        try:
            if not token_embeddings: return OmniResult(error=Exception("Empty"))
            n = len(token_embeddings)
            start_logits = [sum(token_embeddings[i][j]*self.start_weights[j] for j in range(min(len(token_embeddings[i]),self.d))) for i in range(n)]
            end_logits = [sum(token_embeddings[i][j]*self.end_weights[j] for j in range(min(len(token_embeddings[i]),self.d))) for i in range(n)]
            best_score = float('-inf'); best_start = 0; best_end = 0
            for s in range(question_len, n):
                for e in range(s, min(s+self.max_answer_len, n)):
                    score = start_logits[s] + end_logits[e]
                    if score > best_score:
                        best_score = score; best_start = s; best_end = e
            confidence = 1.0/(1.0+math.exp(-best_score)) if best_score != float('-inf') else 0
            return OmniResult(data={"start": best_start, "end": best_end, "score": best_score, "confidence": confidence, "answer_len": best_end-best_start+1})
        except Exception as e: return OmniResult(error=e)

    def sliding_window(self, embeddings: List[List[float]], window_size: int = 384, stride: int = 128) -> OmniResult:
        try:
            n = len(embeddings); windows = []
            for start in range(0, n, stride):
                end = min(start+window_size, n)
                windows.append({"start": start, "end": end, "size": end-start})
                if end >= n: break
            return OmniResult(data={"n_windows": len(windows), "windows": windows, "total_tokens": n})
        except Exception as e: return OmniResult(error=e)
