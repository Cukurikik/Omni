"""
omni_ngram_scorer.py — N-Gram Likelihood Scorer
Layer: Compute / NLP
Inspired by: KenLM / nltk

Implements a statistical N-Gram language model. Calculates the probability
of a sentence occurring based on the historical frequencies of its constituent
N-Grams. Frequently used for rapid spell checking and text generation baseline. Zero mock.
"""

import collections
import math
from typing import List, Dict, Tuple

class OmniNGramScorer:
    def __init__(self, n: int = 3):
        self.n = n
        # Maps an (N-1)-gram context to a dictionary of next-word counts
        self.counts: Dict[Tuple[str, ...], Dict[str, int]] = collections.defaultdict(lambda: collections.defaultdict(int))
        # Total counts of the context to calculate probabilities
        self.context_totals: Dict[Tuple[str, ...], int] = collections.defaultdict(int)
        
        # Vocabulary for Laplace smoothing
        self.vocab = set()

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace tokenizer."""
        return text.lower().split()

    def train(self, corpus: List[str]):
        """
        Trains the N-gram model on a list of sentences.
        """
        for sentence in corpus:
            tokens = self._tokenize(sentence)
            self.vocab.update(tokens)
            
            # Pad sequence with Start and End tokens
            padded_tokens = ["<s>"] * (self.n - 1) + tokens + ["</s>"]
            
            for i in range(len(padded_tokens) - self.n + 1):
                ngram = padded_tokens[i:i+self.n]
                context = tuple(ngram[:-1])
                target = ngram[-1]
                
                self.counts[context][target] += 1
                self.context_totals[context] += 1

    def _get_prob(self, context: Tuple[str, ...], target: str) -> float:
        """
        Calculates P(target | context) using Laplace (Add-1) Smoothing.
        """
        count = self.counts[context].get(target, 0)
        total = self.context_totals[context]
        vocab_size = len(self.vocab)
        
        # Add-1 smoothing to prevent log(0)
        return (count + 1.0) / (total + vocab_size)

    def score_sentence(self, sentence: str) -> float:
        """
        Calculates the log-likelihood of a sentence.
        Higher (closer to 0) is better.
        """
        tokens = self._tokenize(sentence)
        padded_tokens = ["<s>"] * (self.n - 1) + tokens + ["</s>"]
        
        log_prob = 0.0
        
        for i in range(len(padded_tokens) - self.n + 1):
            ngram = padded_tokens[i:i+self.n]
            context = tuple(ngram[:-1])
            target = ngram[-1]
            
            p = self._get_prob(context, target)
            log_prob += math.log(p)
            
        return log_prob

    def perplexity(self, sentence: str) -> float:
        """
        Calculates Perplexity (2^(-1/N * log2(P))). Lower is better.
        """
        tokens = self._tokenize(sentence)
        N = len(tokens) + 1 # Include </s>
        
        if N == 0:
            return float('inf')
            
        log_prob = self.score_sentence(sentence)
        # Convert natural log to base 2
        log2_prob = log_prob / math.log(2)
        
        return 2.0 ** (-log2_prob / N)
