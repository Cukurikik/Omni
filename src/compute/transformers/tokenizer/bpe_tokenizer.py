"""
OMNI Transformer — BPE Tokenizer
Byte-Pair Encoding tokenizer for transformer models.
Learned from: Kaleidophon/token2index, openai/tiktoken
"""
import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import Counter

logger = logging.getLogger(__name__)


class BPETokenizer:
    """Production BPE tokenizer with special token support."""
    def __init__(self, vocab: Optional[Dict[str, int]] = None, merges: Optional[List[Tuple[str, str]]] = None):
        self.vocab = vocab or {}
        self.merges = merges or []
        self.inverse_vocab = {v: k for k, v in self.vocab.items()}
        self.special_tokens = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3, "<mask>": 4}
        self.pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\w+| ?\d+| ?[^\s\w]+|\s+""")

    @property
    def vocab_size(self) -> int:
        return len(self.vocab) + len(self.special_tokens)

    def _get_pairs(self, word: List[str]) -> set:
        return {(word[i], word[i + 1]) for i in range(len(word) - 1)}

    def _bpe(self, token: str) -> List[str]:
        word = list(token)
        if len(word) <= 1:
            return word
        for pair in self.merges:
            new_word = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and (word[i], word[i + 1]) == pair:
                    new_word.append(word[i] + word[i + 1])
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            word = new_word
            if len(word) == 1:
                break
        return word

    def encode(self, text: str, max_length: int = 512, truncation: bool = True,
               padding: bool = False, add_special_tokens: bool = True) -> Dict[str, List[int]]:
        tokens = self.pat.findall(text.lower())
        ids = []
        if add_special_tokens:
            ids.append(self.special_tokens["<bos>"])

        for token in tokens:
            subwords = self._bpe(token)
            for sw in subwords:
                ids.append(self.vocab.get(sw, self.special_tokens["<unk>"]))

        if add_special_tokens:
            ids.append(self.special_tokens["<eos>"])

        if truncation and len(ids) > max_length:
            ids = ids[:max_length]

        attention_mask = [1] * len(ids)
        if padding and len(ids) < max_length:
            pad_len = max_length - len(ids)
            ids.extend([self.special_tokens["<pad>"]] * pad_len)
            attention_mask.extend([0] * pad_len)

        return {"input_ids": ids, "attention_mask": attention_mask}

    def decode(self, ids: List[int]) -> str:
        tokens = []
        for i in ids:
            if i in self.special_tokens.values():
                continue
            tokens.append(self.inverse_vocab.get(i, "<unk>"))
        return "".join(tokens)

    def save(self, path: str) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
        with open(Path(path) / "vocab.json", "w") as f:
            json.dump(self.vocab, f)
        with open(Path(path) / "merges.txt", "w") as f:
            for pair in self.merges:
                f.write(f"{pair[0]} {pair[1]}\n")

    @classmethod
    def load(cls, path: str) -> "BPETokenizer":
        with open(Path(path) / "vocab.json") as f:
            vocab = json.load(f)
        merges = []
        merges_path = Path(path) / "merges.txt"
        if merges_path.exists():
            with open(merges_path) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        merges.append(tuple(parts))
        return cls(vocab=vocab, merges=merges)

    @classmethod
    def train(cls, texts: List[str], vocab_size: int = 32000, min_frequency: int = 2) -> "BPETokenizer":
        """Train BPE tokenizer from corpus."""
        pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\w+| ?\d+| ?[^\s\w]+|\s+""")
        word_freqs = Counter()
        for text in texts:
            for token in pat.findall(text.lower()):
                word_freqs[tuple(token)] += 1

        # Initialize vocab with characters
        chars = set()
        for word in word_freqs:
            for c in word:
                chars.add(c)
        vocab = {c: i + 5 for i, c in enumerate(sorted(chars))}  # Reserve 0-4 for special tokens
        merges = []

        while len(vocab) < vocab_size:
            pairs = Counter()
            for word, freq in word_freqs.items():
                for i in range(len(word) - 1):
                    pairs[(word[i], word[i + 1])] += freq
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            if pairs[best] < min_frequency:
                break
            merges.append(best)
            merged = best[0] + best[1]
            vocab[merged] = len(vocab) + 5

            new_freqs = Counter()
            for word, freq in word_freqs.items():
                new_word = []
                i = 0
                while i < len(word):
                    if i < len(word) - 1 and (word[i], word[i + 1]) == best:
                        new_word.append(merged)
                        i += 2
                    else:
                        new_word.append(word[i])
                        i += 1
                new_freqs[tuple(new_word)] = freq
            word_freqs = new_freqs

        logger.info(f"Trained BPE: {len(vocab)} tokens, {len(merges)} merges")
        return cls(vocab=vocab, merges=merges)
