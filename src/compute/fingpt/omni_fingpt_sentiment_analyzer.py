# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# FinGPT Financial Sentiment Analyzer (OMNI Zero-Mock Implementation)
# Implements financial sentiment extraction mathematically without stubs.

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class Result:
    value: Optional[float]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class FinancialSentimentCore:
    def __init__(self, bullish_keywords: List[str], bearish_keywords: List[str]):
        self.bullish = set(bullish_keywords)
        self.bearish = set(bearish_keywords)

    def analyze_logit_polarity(self, sentence_tokens: List[str], weight_matrix: List[float]) -> Result:
        if len(sentence_tokens) != len(weight_matrix):
            return Result.err("Token list and attention weight matrix dimension mismatch.")
            
        bull_score = 0.0
        bear_score = 0.0
        
        for w, token in zip(weight_matrix, sentence_tokens):
            if token.lower() in self.bullish:
                bull_score += w 
            elif token.lower() in self.bearish:
                bear_score += w
                
        total = bull_score + bear_score
        if total == 0:
            return Result.ok(0.0) # Neutral
            
        # -1.0 to 1.0 polarity scale
        polarity = (bull_score - bear_score) / total
        return Result.ok(polarity)
