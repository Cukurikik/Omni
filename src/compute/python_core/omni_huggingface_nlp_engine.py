"""
OMNI HuggingFace NLP Engine — Transformer NLP pipeline primitives.

Assimilated from: huggingface/course (15k ★)
The Hugging Face course on Transformers.

Implements core NLP building blocks:
  - Tokenization: BPE-like subword, word-level, character-level
  - Text encoding: token-to-id, padding, truncation, attention masks
  - Pipeline stages: preprocessing, model forward, postprocessing
  - Classification head: logits → labels
  - Named Entity Recognition (NER): BIO tag decoding
  - Question Answering: span extraction from logits
  - Text generation: greedy, top-k, top-p (nucleus) sampling

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniHuggingFaceNLPEngine"


class Result:
    """Monadic Result type for error handling."""
    pass

class Ok(Result):
    """Monadic Ok result type."""
    def __init__(self, value: Any) -> None:
        """Initialize Ok."""
        self.value = value

class Err(Result):
    """Monadic Err result type."""
    def __init__(self, error: str) -> None:
        """Initialize Err."""
        self.error = error


class OmniHuggingFaceNLPEngine:
    """Production-grade NLP pipeline engine (HuggingFace Transformers pattern).

    Implements NLP building blocks:
      - Tokenization (BPE-like, word, char)
      - Encoding with padding/truncation/attention masks
      - Classification, NER, QA postprocessing
      - Text generation (greedy, top-k, nucleus)
      - Perplexity computation

    @since 1.0.0
    @tags ["nlp", "transformers", "tokenization", "huggingface", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniHuggingFaceNLPEngine."""
        pass

    def diagnostics(self) -> Result:
        """Performs diagnostics operation for OmniHuggingFaceNLPEngine."""
        return Ok({
            "engine": self.ENGINE_ID, "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "build_vocab", "tokenize_bpe", "encode",
                "classify", "ner_decode", "qa_extract",
                "generate_greedy", "generate_topk", "generate_nucleus",
                "perplexity",
            ],
        })

    # -----------------------------------------------------------------
    # 1. TOKENIZATION
    # -----------------------------------------------------------------

    def build_vocab(self, corpus: List[str], max_vocab: int = 5000) -> Result:
        """Build vocabulary from corpus (word-level).

        @param corpus: List of text strings.
        @param max_vocab: Maximum vocabulary size.
        @returns Result with dict: 'token2id', 'id2token'.
        """
        counts: Counter = Counter()
        for text in corpus:
            for word in text.lower().split():
                counts[word] += 1

        special = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
        token2id = {t: i for i, t in enumerate(special)}
        for word, _ in counts.most_common(max_vocab - len(special)):
            token2id[word] = len(token2id)
        id2token = {v: k for k, v in token2id.items()}
        return Ok({"token2id": token2id, "id2token": id2token})

    def tokenize_words(self, text: str) -> Result:
        """Simple whitespace tokenization with lowercasing.

        @param text: Input string.
        @returns Result with list of tokens.
        """
        return Ok(text.lower().split())

    def tokenize_bpe_like(self, text: str, merges: Dict[str, str]) -> Result:
        """BPE-like subword tokenization using merge rules.

        @param text: Input text.
        @param merges: Dict of (pair_str → merged_token) merge rules.
        @returns Result with list of subword tokens.
        """
        words = text.lower().split()
        result = []
        for word in words:
            chars = list(word)
            # Apply merges iteratively
            for pair_str, merged in merges.items():
                a, b = pair_str.split("+")
                i = 0
                new_chars = []
                while i < len(chars):
                    if i < len(chars) - 1 and chars[i] == a and chars[i + 1] == b:
                        new_chars.append(merged)
                        i += 2
                    else:
                        new_chars.append(chars[i])
                        i += 1
                chars = new_chars
            result.extend(chars)
        return Ok(result)

    # -----------------------------------------------------------------
    # 2. ENCODING
    # -----------------------------------------------------------------

    def encode(
        self, tokens: List[str], token2id: Dict[str, int],
        max_length: int = 128, padding: bool = True, truncation: bool = True
    ) -> Result:
        """Encode tokens to IDs with padding/truncation and attention mask.

        @param tokens: List of tokens.
        @param token2id: Vocabulary mapping.
        @param max_length: Maximum sequence length.
        @param padding: Whether to pad shorter sequences.
        @param truncation: Whether to truncate longer sequences.
        @returns Result with dict: 'input_ids', 'attention_mask'.
        """
        unk_id = token2id.get("[UNK]", 1)
        ids = [token2id.get(t, unk_id) for t in tokens]

        if truncation and len(ids) > max_length:
            ids = ids[:max_length]

        attn_mask = [1] * len(ids)

        if padding and len(ids) < max_length:
            pad_id = token2id.get("[PAD]", 0)
            pad_len = max_length - len(ids)
            ids.extend([pad_id] * pad_len)
            attn_mask.extend([0] * pad_len)

        return Ok({
            "input_ids": np.array(ids, dtype=np.int64),
            "attention_mask": np.array(attn_mask, dtype=np.int64),
        })

    # -----------------------------------------------------------------
    # 3. CLASSIFICATION
    # -----------------------------------------------------------------

    def classify(self, logits: np.ndarray, labels: List[str]) -> Result:
        """Classify from logits (argmax) and return label + confidence.

        @param logits: (C,) or (N, C) raw logits.
        @param labels: List of C label names.
        @returns Result with dict(s): 'label', 'score'.
        """
        if logits.ndim == 1:
            mx = np.max(logits)
            probs = np.exp(logits - mx) / (np.sum(np.exp(logits - mx)) + 1e-10)
            idx = int(np.argmax(probs))
            return Ok({"label": labels[idx], "score": float(probs[idx])})
        elif logits.ndim == 2:
            results = []
            for row in logits:
                mx = np.max(row)
                probs = np.exp(row - mx) / (np.sum(np.exp(row - mx)) + 1e-10)
                idx = int(np.argmax(probs))
                results.append({"label": labels[idx], "score": float(probs[idx])})
            return Ok(results)
        return Err("logits must be 1D or 2D.")

    # -----------------------------------------------------------------
    # 4. NER (BIO Tag Decoding)
    # -----------------------------------------------------------------

    def ner_decode(
        self, token_logits: np.ndarray, tokens: List[str], tag_names: List[str]
    ) -> Result:
        """Decode NER predictions from per-token logits.

        @param token_logits: (T, n_tags) logits per token.
        @param tokens: (T,) original tokens.
        @param tag_names: List of BIO tag names (e.g., ["O", "B-PER", "I-PER"]).
        @returns Result with list of entity dicts.
        """
        if token_logits.shape[0] != len(tokens):
            return Err("token_logits and tokens length mismatch.")

        predictions = np.argmax(token_logits, axis=-1)
        entities = []
        current_entity = None

        for i, (token, pred_idx) in enumerate(zip(tokens, predictions)):
            tag = tag_names[pred_idx] if pred_idx < len(tag_names) else "O"
            if tag.startswith("B-"):
                if current_entity:
                    entities.append(current_entity)
                current_entity = {"entity": tag[2:], "tokens": [token], "start": i}
            elif tag.startswith("I-") and current_entity and tag[2:] == current_entity["entity"]:
                current_entity["tokens"].append(token)
            else:
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None

        if current_entity:
            entities.append(current_entity)
        return Ok(entities)

    # -----------------------------------------------------------------
    # 5. QUESTION ANSWERING
    # -----------------------------------------------------------------

    def qa_extract(
        self, start_logits: np.ndarray, end_logits: np.ndarray,
        tokens: List[str], n_best: int = 5
    ) -> Result:
        """Extract answer span from QA start/end logits.

        @param start_logits: (T,) start position logits.
        @param end_logits: (T,) end position logits.
        @param tokens: (T,) tokens.
        @param n_best: Number of candidate answers.
        @returns Result with list of answer dicts.
        """
        T = len(tokens)
        if len(start_logits) != T or len(end_logits) != T:
            return Err("Logits and tokens length mismatch.")

        # Get top-n start/end positions
        start_idx = np.argsort(start_logits)[::-1][:n_best]
        end_idx = np.argsort(end_logits)[::-1][:n_best]

        answers = []
        for s in start_idx:
            for e in end_idx:
                if e >= s and e - s < 30:  # max answer length
                    score = float(start_logits[s] + end_logits[e])
                    answer = " ".join(tokens[s:e + 1])
                    answers.append({"answer": answer, "score": score, "start": int(s), "end": int(e)})

        answers.sort(key=lambda x: -x["score"])
        return Ok(answers[:n_best])

    # -----------------------------------------------------------------
    # 6. TEXT GENERATION
    # -----------------------------------------------------------------

    def generate_greedy(self, logits_sequence: np.ndarray) -> Result:
        """Greedy decoding: pick argmax at each step.

        @param logits_sequence: (T, V) logits per timestep.
        @returns Result with list of token indices.
        """
        return Ok([int(np.argmax(logits_sequence[t])) for t in range(len(logits_sequence))])

    def generate_topk(
        self, logits: np.ndarray, k: int = 10, temperature: float = 1.0, seed: int = 0
    ) -> Result:
        """Top-k sampling from logits.

        @param logits: (V,) logits for single timestep.
        @param k: Top-k value.
        @param temperature: Sampling temperature.
        @returns Result with sampled token index.
        """
        rng = np.random.RandomState(seed)
        scaled = logits / max(temperature, 1e-6)
        top_k_idx = np.argsort(scaled)[::-1][:k]
        top_k_logits = scaled[top_k_idx]
        mx = np.max(top_k_logits)
        probs = np.exp(top_k_logits - mx)
        probs = probs / (np.sum(probs) + 1e-10)
        chosen = rng.choice(top_k_idx, p=probs)
        return Ok(int(chosen))

    def generate_nucleus(
        self, logits: np.ndarray, p: float = 0.9, temperature: float = 1.0, seed: int = 0
    ) -> Result:
        """Nucleus (top-p) sampling.

        @param logits: (V,) logits.
        @param p: Cumulative probability threshold.
        @param temperature: Sampling temperature.
        @returns Result with sampled token index.
        """
        rng = np.random.RandomState(seed)
        scaled = logits / max(temperature, 1e-6)
        mx = np.max(scaled)
        probs = np.exp(scaled - mx) / (np.sum(np.exp(scaled - mx)) + 1e-10)
        sorted_idx = np.argsort(probs)[::-1]
        sorted_probs = probs[sorted_idx]
        cum_probs = np.cumsum(sorted_probs)
        # Keep tokens until cumulative > p
        cutoff = np.searchsorted(cum_probs, p) + 1
        nucleus_idx = sorted_idx[:cutoff]
        nucleus_probs = probs[nucleus_idx]
        nucleus_probs = nucleus_probs / (np.sum(nucleus_probs) + 1e-10)
        chosen = rng.choice(nucleus_idx, p=nucleus_probs)
        return Ok(int(chosen))

    # -----------------------------------------------------------------
    # 7. PERPLEXITY
    # -----------------------------------------------------------------

    def perplexity(self, log_probs: np.ndarray) -> Result:
        """Compute perplexity from log-probabilities.

        PPL = exp(-1/N * sum(log_probs))

        @param log_probs: (N,) log-probabilities of each token.
        @returns Result with scalar perplexity.
        """
        if len(log_probs) == 0:
            return Err("Empty log_probs.")
        avg = -np.mean(log_probs)
        return Ok(float(np.exp(avg)))
