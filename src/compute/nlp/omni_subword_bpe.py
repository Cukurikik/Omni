"""
omni_subword_bpe.py — Byte-Pair Encoding Tokenizer
Layer: Compute / NLP
Inspired by: OpenAI Tiktoken / HuggingFace Tokenizers

Implements the core training and inference logic for a BPE Tokenizer.
Iteratively merges the most frequent adjacent character/byte pairs into single
tokens, creating an optimal subword vocabulary for LLM processing. Zero mock.
"""

import collections
import re
from typing import List, Dict, Tuple

class OmniBPETokenizer:
    def __init__(self, vocab_size: int):
        self.vocab_size = vocab_size
        self.merges: Dict[Tuple[int, int], int] = {}
        self.vocab: Dict[int, bytes] = {}
        
        # Base vocabulary is the 256 byte values
        for i in range(256):
            self.vocab[i] = bytes([i])

    def _get_stats(self, ids: List[int]) -> Dict[Tuple[int, int], int]:
        """Counts frequencies of consecutive pairs."""
        counts = collections.defaultdict(int)
        for pair in zip(ids, ids[1:]):
            counts[pair] += 1
        return counts

    def _merge(self, ids: List[int], pair: Tuple[int, int], idx: int) -> List[int]:
        """Replaces all occurrences of `pair` in `ids` with the new `idx`."""
        new_ids = []
        i = 0
        while i < len(ids):
            # Check if we found the pair
            if i < len(ids) - 1 and ids[i] == pair[0] and ids[i+1] == pair[1]:
                new_ids.append(idx)
                i += 2
            else:
                new_ids.append(ids[i])
                i += 1
        return new_ids

    def train(self, text: str):
        """
        Trains the BPE vocabulary on a raw text string.
        """
        # 1. Convert text to raw UTF-8 bytes (base tokens)
        text_bytes = text.encode("utf-8")
        ids = list(text_bytes)

        # 2. Iteratively merge the most frequent pairs
        num_merges = self.vocab_size - 256
        
        for i in range(num_merges):
            stats = self._get_stats(ids)
            if not stats:
                break
                
            # Find the most frequent pair
            best_pair = max(stats, key=stats.get)
            
            # Assign a new token ID
            new_idx = 256 + i
            
            # Record the merge rule
            self.merges[best_pair] = new_idx
            self.vocab[new_idx] = self.vocab[best_pair[0]] + self.vocab[best_pair[1]]
            
            # Apply merge to the training data
            ids = self._merge(ids, best_pair, new_idx)

    def encode(self, text: str) -> List[int]:
        """
        Encodes a string into a list of BPE token IDs.
        """
        text_bytes = text.encode("utf-8")
        ids = list(text_bytes)
        
        # Keep merging until no more merge rules apply
        while len(ids) >= 2:
            stats = self._get_stats(ids)
            
            # Find the pair in current `ids` that has the lowest merge index (was merged earliest)
            pair = min(stats.keys(), key=lambda p: self.merges.get(p, float("inf")))
            
            # If the best pair is not in our learned merges, we are done
            if pair not in self.merges:
                break
                
            idx = self.merges[pair]
            ids = self._merge(ids, pair, idx)
            
        return ids

    def decode(self, ids: List[int]) -> str:
        """
        Decodes a list of token IDs back into a string.
        """
        b = b"".join(self.vocab[idx] for idx in ids)
        return b.decode("utf-8", errors="replace")
