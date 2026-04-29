# langkit — LLM Output Quality Metrics
from typing import Optional, Generic, TypeVar, Dict
import math, re
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class LangkitAnalyzer:
    MAX_TEXT = 100000
    def analyze(self, text: str) -> OmniResult[Dict, str]:
        if not text: return OmniResult(error="Empty text")
        if len(text) > self.MAX_TEXT: return OmniResult(error=f"Text exceeds {self.MAX_TEXT}")
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        char_count = len(text)
        word_count = len(words)
        sent_count = max(1, len([s for s in sentences if s.strip()]))
        avg_word_len = sum(len(w) for w in words) / max(1, word_count)
        flesch = 206.835 - 1.015*(word_count/sent_count) - 84.6*(sum(len(w) for w in words)/(word_count*max(1,sent_count)))
        return OmniResult(value={
            "char_count": char_count, "word_count": word_count, "sentence_count": sent_count,
            "avg_word_length": round(avg_word_len, 2), "flesch_readability": round(max(0, flesch), 2),
        })

    def detect_hallucination_signals(self, response: str, context: str) -> OmniResult[Dict, str]:
        if not response or not context: return OmniResult(error="Empty response or context")
        resp_words = set(response.lower().split())
        ctx_words = set(context.lower().split())
        overlap = len(resp_words & ctx_words)
        coverage = overlap / max(1, len(resp_words))
        return OmniResult(value={"grounding_score": round(coverage, 4), "novel_ratio": round(1 - coverage, 4)})
