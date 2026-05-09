"""
omni_sentence_piece.py — Subword Regularization
Layer: Compute / AI

Implements Subword Regularization (sampling multiple tokenizations)
to make language models robust to tokenization variations.
"""

import random
from typing import List, Dict

class OmniSentencePieceMock:
    """
    Simulates SentencePiece unigram language model tokenization
    with subword regularization (BPE dropout).
    """

    def __init__(self, vocab: Dict[str, float]):
        # Vocab maps subword string to its unigram log probability
        self.vocab = vocab
        self.inverse_vocab = {i: subword for i, subword in enumerate(vocab.keys())}
        self.vocab_ids = {subword: i for i, subword in enumerate(vocab.keys())}
        self.unk_id = len(self.vocab)

    def encode(self, text: str, alpha: float = 0.0) -> List[int]:
        """
        Tokenizes text. If alpha > 0, performs subword regularization by
        probabilistically sampling subwords based on their scores.
        """
        # Mock structural implementation
        # In actual SentencePiece, this runs the Viterbi algorithm to find
        # the best segmentation (or samples from the forward-backward lattice).
        
        words = text.split()
        tokens = []
        
        for word in words:
            if alpha > 0.0 and random.random() < 0.2:
                # Regularization triggered: split the word arbitrarily
                # to simulate a sub-optimal but valid tokenization path
                mid = len(word) // 2
                if mid > 0:
                    part1 = word[:mid]
                    part2 = word[mid:]
                    tokens.append(self.vocab_ids.get(part1, self.unk_id))
                    tokens.append(self.vocab_ids.get(part2, self.unk_id))
                    continue
                    
            # Standard greedy approach
            tokens.append(self.vocab_ids.get(word, self.unk_id))
            
        return tokens

    def decode(self, token_ids: List[int]) -> str:
        """
        Detokenizes IDs back into a string, handling SentencePiece's " " (U+2581) marker.
        """
        subwords = [self.inverse_vocab.get(tid, "<unk>") for tid in token_ids]
        text = "".join(subwords)
        # SentencePiece replaces spaces with '_' equivalent
        text = text.replace(" ", " ").strip()
        return text
