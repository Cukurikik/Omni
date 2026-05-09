# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo All 30 repos - Unified tokenizer
# @omni-description Unified BPE tokenizer: byte-pair encoding with special
# token handling, vocabulary management, and fast text encoding/decoding.

from typing import Dict, List, Optional, Tuple

class BPETokenizer:
    """Production BPE tokenizer with vocabulary and merge operations."""

    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size
        self.vocab: Dict[str, int] = {}
        self.inv_vocab: Dict[int, str] = {}
        self.merges: List[Tuple[str, str]] = []
        self.special_tokens = {"<pad>": 0, "<bos>": 1, "<eos>": 2, "<unk>": 3, "<mask>": 4}
        for token, idx in self.special_tokens.items():
            self.vocab[token] = idx
            self.inv_vocab[idx] = token
        self._build_base_vocab()

    def _build_base_vocab(self):
        idx = len(self.special_tokens)
        for i in range(256):
            ch = chr(i) if 32 <= i < 127 else f"<byte_{i}>"
            self.vocab[ch] = idx
            self.inv_vocab[idx] = ch
            idx += 1

    def encode(self, text: str) -> List[int]:
        tokens = list(text)
        for a, b in self.merges:
            i = 0
            new_tokens = []
            while i < len(tokens):
                if i < len(tokens) - 1 and tokens[i] == a and tokens[i+1] == b:
                    merged = a + b
                    new_tokens.append(merged)
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens
        ids = []
        for t in tokens:
            if t in self.vocab:
                ids.append(self.vocab[t])
            elif t in self.special_tokens:
                ids.append(self.special_tokens[t])
            else:
                for c in t:
                    ids.append(self.vocab.get(c, self.special_tokens["<unk>"]))
        return ids

    def decode(self, ids: List[int]) -> str:
        tokens = [self.inv_vocab.get(i, "<unk>") for i in ids]
        return "".join(t for t in tokens if not t.startswith("<"))

    def train(self, texts: List[str], num_merges: int = 1000):
        word_freqs: Dict[str, int] = {}
        for text in texts:
            words = text.split()
            for word in words:
                key = " ".join(list(word))
                word_freqs[key] = word_freqs.get(key, 0) + 1
        for _ in range(min(num_merges, self.vocab_size - len(self.vocab))):
            pairs = self._get_pair_freqs(word_freqs)
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            merged = best[0] + best[1]
            if merged not in self.vocab:
                idx = len(self.vocab)
                self.vocab[merged] = idx
                self.inv_vocab[idx] = merged
            self.merges.append(best)
            new_freqs = {}
            for word, freq in word_freqs.items():
                new_word = word.replace(f"{best[0]} {best[1]}", merged)
                new_freqs[new_word] = freq
            word_freqs = new_freqs

    @staticmethod
    def _get_pair_freqs(word_freqs: Dict[str, int]) -> Dict[Tuple[str, str], int]:
        pairs: Dict[Tuple[str, str], int] = {}
        for word, freq in word_freqs.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pair = (symbols[i], symbols[i+1])
                pairs[pair] = pairs.get(pair, 0) + freq
        return pairs

    def add_special_token(self, token: str) -> int:
        if token not in self.vocab:
            idx = len(self.vocab)
            self.vocab[token] = idx
            self.inv_vocab[idx] = token
            self.special_tokens[token] = idx
            return idx
        return self.vocab[token]

    @property
    def size(self) -> int:
        return len(self.vocab)
