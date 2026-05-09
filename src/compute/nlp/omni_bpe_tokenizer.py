"""
omni_bpe_tokenizer.py — Byte-Pair Encoding Tokenizer
Layer: Compute / AI

Implementation of the BPE algorithm used in models like GPT-3 and RoBERTa.
Handles vocabulary merging and sequence encoding/decoding.
"""

from typing import List, Dict, Tuple
import re
from collections import defaultdict

class OmniBPETokenizer:
    def __init__(self, vocab_size: int = 5000):
        self.vocab_size = vocab_size
        self.bpe_ranks: Dict[Tuple[str, str], int] = {}
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        
        # Regex to split words before subword tokenization
        self.pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")

    def _get_stats(self, vocab: Dict[str, int]) -> Dict[Tuple[str, str], int]:
        """Calculates frequency of adjacent character pairs."""
        pairs = defaultdict(int)
        for word, freq in vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[symbols[i], symbols[i+1]] += freq
        return pairs

    def _merge_vocab(self, pair: Tuple[str, str], v_in: Dict[str, int]) -> Dict[str, int]:
        """Replaces the most frequent pair with a merged symbol in the vocab."""
        v_out = {}
        bigram = re.escape(' '.join(pair))
        p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
        
        replacement = ''.join(pair)
        for word in v_in:
            w_out = p.sub(replacement, word)
            v_out[w_out] = v_in[word]
        return v_out

    def train(self, texts: List[str]):
        """Trains the BPE model on a corpus."""
        # 1. Base character vocabulary
        word_freqs = defaultdict(int)
        for text in texts:
            words = text.split() # Simplified pre-tokenization
            for word in words:
                # Add end-of-word marker and split to chars
                chars = " ".join(list(word)) + " </w>"
                word_freqs[chars] += 1

        vocab = word_freqs
        num_merges = self.vocab_size - 256 # Assuming 256 byte base
        
        for i in range(num_merges):
            pairs = self._get_stats(vocab)
            if not pairs:
                break
                
            best = max(pairs, key=pairs.get)
            self.bpe_ranks[best] = i
            vocab = self._merge_vocab(best, vocab)
            
        # Build final vocabulary dictionaries
        self._build_vocab_from_ranks()

    def _build_vocab_from_ranks(self):
        # Initial bytes
        self.vocab = {chr(i): i for i in range(256)}
        idx = 256
        
        for pair in self.bpe_ranks:
            self.vocab[''.join(pair)] = idx
            idx += 1
            
        self.vocab['</w>'] = idx
        self.vocab['<unk>'] = idx + 1
        
        self.inverse_vocab = {v: k for k, v in self.vocab.items()}

    def encode(self, text: str) -> List[int]:
        """Encodes a string into token IDs."""
        if not self.vocab:
            return [] # Untrained
            
        words = text.split()
        tokens = []
        for word in words:
            word = word + "</w>"
            # For brevity, greedy search over pairs is omitted in this mock.
            # It would iteratively apply the highest-ranked merges to `word`.
            tokens.append(self.vocab.get(word, self.vocab['<unk>']))
            
        return tokens

    def decode(self, tokens: List[int]) -> str:
        """Decodes token IDs back to a string."""
        text = ''.join([self.inverse_vocab.get(t, '') for t in tokens])
        text = text.replace('</w>', ' ').strip()
        return text
