"""
omni_vocab_tokenizer.py — BPE Tokenizer for OMNI Models
Inspired by: SentencePiece/tiktoken for Bio-NER/text tasks
Layer: Compute / NLP

Byte-pair encoding tokenizer with special token support,
vocabulary management, and efficient encoding/decoding.
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class TokenizerConfig:
    vocab_size: int = 32000
    min_frequency: int = 2
    special_tokens: List[str] = field(default_factory=lambda: [
        "<pad>", "<unk>", "<bos>", "<eos>", "<mask>",
        "<sep>", "<cls>", "<bio_b>", "<bio_i>", "<bio_o>",
    ])
    max_token_length: int = 50
    byte_fallback: bool = True
    lowercase: bool = False


class BPEMerge:
    """Represents a single BPE merge operation."""
    __slots__ = ["pair", "new_token", "rank"]

    def __init__(self, pair: Tuple[str, str], new_token: str, rank: int):
        self.pair = pair
        self.new_token = new_token
        self.rank = rank


class OmniVocabTokenizer:
    """Production BPE tokenizer for OMNI NLP models.

    Features:
    - Byte-pair encoding with configurable vocabulary size
    - Special token management for Bio-NER and sequence tasks
    - JSON serialization for model checkpoints
    - Efficient batch encoding/decoding
    """

    def __init__(self, config: TokenizerConfig = TokenizerConfig()):
        self.config = config
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}
        self.merges: List[BPEMerge] = []
        self.merge_ranks: Dict[Tuple[str, str], int] = {}

        # Initialize special tokens
        for idx, token in enumerate(config.special_tokens):
            self.token_to_id[token] = idx
            self.id_to_token[idx] = token

        self._next_id = len(config.special_tokens)
        self.pad_id = self.token_to_id.get("<pad>", 0)
        self.unk_id = self.token_to_id.get("<unk>", 1)
        self.bos_id = self.token_to_id.get("<bos>", 2)
        self.eos_id = self.token_to_id.get("<eos>", 3)
        self.mask_id = self.token_to_id.get("<mask>", 4)

    @property
    def vocab_size(self) -> int:
        return len(self.token_to_id)

    def _pre_tokenize(self, text: str) -> List[str]:
        """Split text into pre-tokens using regex."""
        if self.config.lowercase:
            text = text.lower()
        # GPT-2 style pre-tokenization
        pattern = r"""'s|'t|'re|'ve|'m|'ll|'d| ?\w+| ?\d+| ?[^\s\w\d]+|\s+(?!\S)|\s+"""
        return re.findall(pattern, text)

    def _get_pairs(self, word: List[str]) -> Set[Tuple[str, str]]:
        """Get all adjacent character pairs in a word."""
        pairs = set()
        for i in range(len(word) - 1):
            pairs.add((word[i], word[i + 1]))
        return pairs

    def train(self, texts: List[str]):
        """Train BPE tokenizer on corpus."""
        # Count character-level frequencies
        word_freqs: Dict[Tuple[str, ...], int] = defaultdict(int)

        for text in texts:
            pre_tokens = self._pre_tokenize(text)
            for token in pre_tokens:
                chars = tuple(token)
                word_freqs[chars] += 1

        # Add individual characters to vocab
        char_set = set()
        for word in word_freqs:
            for char in word:
                char_set.add(char)

        for char in sorted(char_set):
            if char not in self.token_to_id:
                self.token_to_id[char] = self._next_id
                self.id_to_token[self._next_id] = char
                self._next_id += 1

        # Perform BPE merges
        words = {word: freq for word, freq in word_freqs.items()}

        while self.vocab_size < self.config.vocab_size:
            # Count pair frequencies
            pair_freqs: Dict[Tuple[str, str], int] = defaultdict(int)
            for word, freq in words.items():
                word_list = list(word)
                for pair in self._get_pairs(word_list):
                    pair_freqs[pair] += freq

            if not pair_freqs:
                break

            # Find most frequent pair
            best_pair = max(pair_freqs, key=pair_freqs.get)
            if pair_freqs[best_pair] < self.config.min_frequency:
                break

            # Create new merged token
            new_token = best_pair[0] + best_pair[1]
            if len(new_token) > self.config.max_token_length:
                break

            merge = BPEMerge(best_pair, new_token, len(self.merges))
            self.merges.append(merge)
            self.merge_ranks[best_pair] = merge.rank

            # Add to vocabulary
            if new_token not in self.token_to_id:
                self.token_to_id[new_token] = self._next_id
                self.id_to_token[self._next_id] = new_token
                self._next_id += 1

            # Apply merge to all words
            new_words = {}
            for word, freq in words.items():
                new_word = self._apply_merge(list(word), best_pair, new_token)
                new_words[tuple(new_word)] = freq
            words = new_words

        logger.info(f"Training complete: {self.vocab_size} tokens, {len(self.merges)} merges")

    def _apply_merge(self, word: List[str], pair: Tuple[str, str],
                     new_token: str) -> List[str]:
        """Apply a single merge to a word."""
        result = []
        i = 0
        while i < len(word):
            if i < len(word) - 1 and word[i] == pair[0] and word[i + 1] == pair[1]:
                result.append(new_token)
                i += 2
            else:
                result.append(word[i])
                i += 1
        return result

    def _bpe_encode_word(self, word: str) -> List[str]:
        """Apply BPE merges to a single word."""
        tokens = list(word)

        while len(tokens) > 1:
            pairs = self._get_pairs(tokens)
            ranked = [(p, self.merge_ranks.get(p, float("inf"))) for p in pairs]
            best = min(ranked, key=lambda x: x[1])

            if best[1] == float("inf"):
                break

            merge = self.merges[best[1]]
            tokens = self._apply_merge(tokens, merge.pair, merge.new_token)

        return tokens

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """Encode text to token IDs."""
        pre_tokens = self._pre_tokenize(text)
        ids = []

        if add_special_tokens:
            ids.append(self.bos_id)

        for pre_token in pre_tokens:
            bpe_tokens = self._bpe_encode_word(pre_token)
            for token in bpe_tokens:
                token_id = self.token_to_id.get(token, self.unk_id)
                ids.append(token_id)

        if add_special_tokens:
            ids.append(self.eos_id)

        return ids

    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs back to text."""
        special_ids = set(range(len(self.config.special_tokens)))
        tokens = []

        for token_id in ids:
            if skip_special_tokens and token_id in special_ids:
                continue
            token = self.id_to_token.get(token_id, "")
            tokens.append(token)

        return "".join(tokens)

    def batch_encode(self, texts: List[str], max_length: Optional[int] = None,
                     padding: bool = True) -> Dict[str, List[List[int]]]:
        """Batch encode with padding."""
        encoded = [self.encode(text) for text in texts]

        if max_length:
            encoded = [ids[:max_length] for ids in encoded]

        if padding:
            max_len = max(len(ids) for ids in encoded) if encoded else 0
            attention_mask = []
            for i in range(len(encoded)):
                mask = [1] * len(encoded[i]) + [0] * (max_len - len(encoded[i]))
                encoded[i] = encoded[i] + [self.pad_id] * (max_len - len(encoded[i]))
                attention_mask.append(mask)
        else:
            attention_mask = [[1] * len(ids) for ids in encoded]

        return {"input_ids": encoded, "attention_mask": attention_mask}

    def save(self, path: str):
        """Save tokenizer to JSON file."""
        data = {
            "config": {
                "vocab_size": self.config.vocab_size,
                "min_frequency": self.config.min_frequency,
                "special_tokens": self.config.special_tokens,
                "max_token_length": self.config.max_token_length,
            },
            "vocab": self.token_to_id,
            "merges": [(m.pair[0], m.pair[1], m.new_token) for m in self.merges],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "OmniVocabTokenizer":
        """Load tokenizer from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        config = TokenizerConfig(**data["config"])
        tokenizer = cls(config)
        tokenizer.token_to_id = data["vocab"]
        tokenizer.id_to_token = {int(v): k for k, v in data["vocab"].items()}
        tokenizer.merges = [
            BPEMerge((m[0], m[1]), m[2], i)
            for i, m in enumerate(data["merges"])
        ]
        tokenizer.merge_ranks = {
            m.pair: m.rank for m in tokenizer.merges
        }
        tokenizer._next_id = max(tokenizer.id_to_token.keys()) + 1
        return tokenizer
