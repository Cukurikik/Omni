# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Gensim Word2Vec Trainer (OMNI Zero-Mock Implementation)
# Implements Skip-gram mathematics with negative sampling.

from dataclasses import dataclass
from typing import List, Dict, Optional
import math

@dataclass
class Result:
    value: Optional[Dict[str, List[float]]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: Dict[str, List[float]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class Word2VecSkipGram:
    def __init__(self, vocab_size: int, vector_size: int, lr: float = 0.025):
        self.vocab_size = vocab_size
        self.vector_size = vector_size
        self.lr = lr
        self.vectors = [[0.1] * vector_size for _ in range(vocab_size)]

    def sigmoid(self, x: float) -> float:
        if x > 6.0: return 1.0
        elif x < -6.0: return 0.0
        return 1.0 / (1.0 + math.exp(-x))

    def train_pair(self, target_id: int, context_id: int, label: int) -> Result:
        if target_id >= self.vocab_size or context_id >= self.vocab_size:
            return Result.err("Out of vocabulary index.")
            
        f = 0.0
        for i in range(self.vector_size):
            f += self.vectors[target_id][i] * self.vectors[context_id][i]
            
        g = (label - self.sigmoid(f)) * self.lr
        
        for i in range(self.vector_size):
            self.vectors[target_id][i] += g * self.vectors[context_id][i]
            self.vectors[context_id][i] += g * self.vectors[target_id][i]
            
        return Result.ok(None)

    def get_embeddings(self, vocab_map: Dict[str, int]) -> Result:
        result_map = {}
        for word, idx in vocab_map.items():
            if idx >= self.vocab_size:
                return Result.err(f"Word {word} index out of bounds.")
            result_map[word] = self.vectors[idx]
        return Result.ok(result_map)
