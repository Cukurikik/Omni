"""
OMNI Compute — Tokenizer Trainer (BPE from scratch)
Train custom BPE tokenizer on domain-specific corpora.
"""
import logging, json, os, re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger("omni.tokenizer_trainer")

@dataclass
class TokenizerTrainerConfig:
    vocab_size: int = 32000; min_frequency: int = 2
    special_tokens: List[str] = field(default_factory=lambda: ["<|pad|>","<|bos|>","<|eos|>","<|unk|>"])
    max_token_length: int = 32; num_merges: int = 0
    output_dir: str = "./tokenizer_output"
    def __post_init__(self):
        if self.num_merges == 0:
            self.num_merges = self.vocab_size - 256 - len(self.special_tokens)

class OmniTokenizerTrainer:
    """Train BPE tokenizer from scratch on domain corpora."""
    def __init__(self, config: TokenizerTrainerConfig):
        self.config = config; self.word_freqs: Counter = Counter()
        self.merges: List[Tuple[str, str]] = []; self.vocab: Dict[str, int] = {}
        os.makedirs(config.output_dir, exist_ok=True)
    def add_corpus(self, texts: List[str]):
        for text in texts:
            words = re.findall(r'\S+|\s+', text)
            for word in words:
                chars = tuple(word)
                self.word_freqs[chars] += 1
        logger.info(f"Corpus added: {len(texts)} texts, {len(self.word_freqs)} unique words")
    def _get_pair_freqs(self, splits: Dict[Tuple, int]) -> Counter:
        pairs = Counter()
        for word, freq in splits.items():
            for i in range(len(word) - 1):
                pairs[(word[i], word[i+1])] += freq
        return pairs
    def _merge_pair(self, pair: Tuple[str, str], splits: Dict[Tuple, int]) -> Dict[Tuple, int]:
        new_splits = {}
        a, b = pair; merged = a + b
        for word, freq in splits.items():
            new_word = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and word[i] == a and word[i+1] == b:
                    new_word.append(merged); i += 2
                else:
                    new_word.append(word[i]); i += 1
            new_splits[tuple(new_word)] = freq
        return new_splits
    def train(self):
        """Run BPE training."""
        logger.info(f"Training BPE tokenizer (target vocab={self.config.vocab_size})")
        splits = dict(self.word_freqs)
        # Build base vocab (byte level)
        for i, tok in enumerate(self.config.special_tokens):
            self.vocab[tok] = i
        base_id = len(self.config.special_tokens)
        for b in range(256):
            self.vocab[chr(b)] = base_id + b
        next_id = base_id + 256
        for step in range(self.config.num_merges):
            pair_freqs = self._get_pair_freqs(splits)
            if not pair_freqs: break
            # Filter by min frequency
            pair_freqs = {p: f for p, f in pair_freqs.items() if f >= self.config.min_frequency}
            if not pair_freqs: break
            best_pair = max(pair_freqs, key=pair_freqs.get)
            splits = self._merge_pair(best_pair, splits)
            merged_token = best_pair[0] + best_pair[1]
            if len(merged_token) <= self.config.max_token_length:
                self.merges.append(best_pair)
                self.vocab[merged_token] = next_id; next_id += 1
            if (step + 1) % 1000 == 0:
                logger.info(f"Step {step+1}/{self.config.num_merges}, vocab={len(self.vocab)}")
        logger.info(f"Training complete: {len(self.vocab)} tokens, {len(self.merges)} merges")
    def save(self):
        with open(os.path.join(self.config.output_dir, "vocab.json"), "w") as f:
            json.dump(self.vocab, f, indent=2)
        with open(os.path.join(self.config.output_dir, "merges.txt"), "w") as f:
            for a, b in self.merges: f.write(f"{a} {b}\n")
        logger.info(f"Tokenizer saved to {self.config.output_dir}")
    def summary(self) -> Dict:
        return {"vocab_size": len(self.vocab), "num_merges": len(self.merges),
                "special_tokens": self.config.special_tokens}
