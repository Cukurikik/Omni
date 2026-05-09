"""
OMNI Transformer — Tokenizer Trainer Pipeline
Train BPE/WordPiece tokenizers from corpus data.
"""
import re
from typing import List, Dict, Optional
from collections import Counter
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WordPieceTrainer:
    """Train WordPiece tokenizer (BERT-style)."""
    def __init__(self, vocab_size: int = 30522, min_frequency: int = 2,
                 special_tokens: Optional[List[str]] = None):
        self.vocab_size = vocab_size
        self.min_frequency = min_frequency
        self.special_tokens = special_tokens or ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]

    def train(self, texts: List[str]) -> Dict[str, int]:
        """Train WordPiece vocabulary from texts."""
        # Pre-tokenize
        word_freqs = Counter()
        for text in texts:
            words = text.lower().split()
            for word in words:
                word_freqs[word] += 1

        # Initialize with character vocabulary
        chars = set()
        for word in word_freqs:
            for c in word:
                chars.add(c)

        vocab = {t: i for i, t in enumerate(self.special_tokens)}
        for c in sorted(chars):
            vocab[c] = len(vocab)
            vocab[f"##{c}"] = len(vocab)

        # Split words into characters with ## prefix
        splits = {}
        for word in word_freqs:
            split = [word[0]] + [f"##{c}" for c in word[1:]]
            splits[word] = split

        # Iteratively merge most frequent pairs
        while len(vocab) < self.vocab_size:
            pair_freqs = Counter()
            for word, freq in word_freqs.items():
                split = splits[word]
                for i in range(len(split) - 1):
                    pair = (split[i], split[i + 1])
                    pair_freqs[pair] += freq

            if not pair_freqs:
                break

            best_pair = max(pair_freqs, key=pair_freqs.get)
            if pair_freqs[best_pair] < self.min_frequency:
                break

            # Merge
            merged = best_pair[0] + best_pair[1].lstrip("##") if best_pair[1].startswith("##") else best_pair[0] + best_pair[1]
            if merged not in vocab:
                vocab[merged] = len(vocab)

            # Update splits
            for word in splits:
                split = splits[word]
                new_split = []
                i = 0
                while i < len(split):
                    if i < len(split) - 1 and (split[i], split[i + 1]) == best_pair:
                        new_split.append(merged)
                        i += 2
                    else:
                        new_split.append(split[i])
                        i += 1
                splits[word] = new_split

        logger.info(f"Trained WordPiece: {len(vocab)} tokens")
        return vocab


class SentencePieceConfig:
    """Configuration for SentencePiece-style unigram tokenizer."""
    def __init__(self, vocab_size: int = 32000, character_coverage: float = 0.9995):
        self.vocab_size = vocab_size
        self.character_coverage = character_coverage


def save_tokenizer(vocab: Dict[str, int], path: str, tokenizer_type: str = "wordpiece") -> None:
    """Save tokenizer vocabulary to disk."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"type": tokenizer_type, "vocab_size": len(vocab), "vocab": vocab}, f, ensure_ascii=False, indent=2)
    logger.info(f"Tokenizer saved: {path} ({len(vocab)} tokens)")


def load_tokenizer(path: str) -> Dict[str, int]:
    """Load tokenizer vocabulary."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["vocab"]
