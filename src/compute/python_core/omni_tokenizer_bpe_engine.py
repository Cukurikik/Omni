"""OmniTokenizerBpeEngine — Production-grade Byte Pair Encoding tokenizer.

Implements BPE tokenization from scratch: frequency-based pair merging,
vocabulary building, and text encoding/decoding.
"""
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniTokenizerBpeEngine:
    """Production engine for Byte Pair Encoding tokenization."""

    ENGINE_VERSION = "1.0.0"

    def _get_pairs(self, tokens: List[str]) -> Dict[Tuple[str, str], int]:
        """Count adjacent pair frequencies."""
        pairs = {}
        for i in range(len(tokens) - 1):
            pair = (tokens[i], tokens[i + 1])
            pairs[pair] = pairs.get(pair, 0) + 1
        return pairs

    def _merge_pair(self, tokens: List[str], pair: Tuple[str, str]) -> List[str]:
        """Merge all occurrences of a pair in the token list."""
        merged = pair[0] + pair[1]
        result = []
        i = 0
        while i < len(tokens):
            if i < len(tokens) - 1 and tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
                result.append(merged)
                i += 2
            else:
                result.append(tokens[i])
                i += 1
        return result

    def train(self, text: str, num_merges: int = 20) -> Result:
        """
        Train BPE vocabulary on given text.

        Args:
            text: Training corpus.
            num_merges: Number of merge operations to perform.

        Returns:
            Result with vocabulary, merge rules, and final tokens.
        """
        try:
            if not text:
                return Err(ValueError("Training text must be non-empty."))
            if num_merges < 0:
                return Err(ValueError("num_merges must be non-negative."))

            tokens = list(text)
            merge_rules = []

            for _ in range(num_merges):
                pairs = self._get_pairs(tokens)
                if not pairs:
                    break
                best_pair = max(pairs, key=pairs.get)
                tokens = self._merge_pair(tokens, best_pair)
                merge_rules.append({"pair": list(best_pair), "merged": best_pair[0] + best_pair[1],
                                     "frequency": pairs[best_pair]})

            vocab = sorted(set(tokens))
            return Ok({"vocabulary": vocab, "vocab_size": len(vocab), "merge_rules": merge_rules,
                        "total_merges": len(merge_rules), "final_tokens": tokens,
                        "final_token_count": len(tokens), "compression_ratio": round(len(text) / max(len(tokens), 1), 4)})
        except Exception as e:
            return Err(e)

    def encode(self, text: str, merge_rules: List[Dict]) -> Result:
        """Encode text using trained merge rules."""
        try:
            tokens = list(text)
            for rule in merge_rules:
                pair = tuple(rule["pair"])
                tokens = self._merge_pair(tokens, pair)
            return Ok({"tokens": tokens, "token_count": len(tokens)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniTokenizerBpeEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N*M) BPE training with M merges"}
