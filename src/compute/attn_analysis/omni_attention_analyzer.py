# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo All 30 repos
# @omni-description Transformer attention pattern analyzer: detects attention
# heads specialized for syntactic, semantic, positional, and copy patterns.

import math
from typing import Dict, List, Tuple

class AttentionPatternAnalyzer:
    """Analyze and classify attention head specialization patterns."""

    def __init__(self, n_layers: int = 12, n_heads: int = 12):
        self.n_layers = n_layers
        self.n_heads = n_heads

    def analyze_head(self, weights: List[List[float]]) -> Dict:
        n = len(weights)
        entropy = self._entropy(weights)
        diag_score = self._diagonal_score(weights)
        prev_score = self._previous_token_score(weights)
        first_score = self._first_token_score(weights)
        uniform_score = self._uniformity_score(weights)
        pattern = self._classify_pattern(diag_score, prev_score, first_score, entropy, uniform_score)
        return {
            "entropy": entropy,
            "diagonal_score": diag_score,
            "previous_token_score": prev_score,
            "first_token_score": first_score,
            "uniformity": uniform_score,
            "pattern": pattern,
        }

    def analyze_all_heads(self, all_weights: List[List[List[List[float]]]]) -> List[List[Dict]]:
        results = []
        for l in range(min(self.n_layers, len(all_weights))):
            layer_results = []
            for h in range(min(self.n_heads, len(all_weights[l]))):
                layer_results.append(self.analyze_head(all_weights[l][h]))
            results.append(layer_results)
        return results

    def _entropy(self, weights: List[List[float]]) -> float:
        entropies = []
        for row in weights:
            h = -sum(p * math.log2(max(p, 1e-10)) for p in row)
            entropies.append(h)
        return sum(entropies) / len(entropies) if entropies else 0

    def _diagonal_score(self, weights: List[List[float]]) -> float:
        n = len(weights)
        if n == 0: return 0
        total = sum(weights[i][i] for i in range(n))
        return total / n

    def _previous_token_score(self, weights: List[List[float]]) -> float:
        n = len(weights)
        if n < 2: return 0
        total = sum(weights[i][i-1] for i in range(1, n))
        return total / (n - 1)

    def _first_token_score(self, weights: List[List[float]]) -> float:
        n = len(weights)
        if n == 0: return 0
        return sum(row[0] for row in weights) / n

    def _uniformity_score(self, weights: List[List[float]]) -> float:
        n = len(weights)
        if n == 0: return 0
        max_entropy = math.log2(n) if n > 1 else 1
        avg_entropy = self._entropy(weights)
        return avg_entropy / max_entropy if max_entropy > 0 else 0

    def _classify_pattern(self, diag: float, prev: float, first: float, entropy: float, uniform: float) -> str:
        if diag > 0.5: return "identity"
        if prev > 0.4: return "previous_token"
        if first > 0.3: return "first_token_sink"
        if uniform > 0.85: return "uniform"
        if entropy < 1.5: return "sparse_focused"
        return "mixed"

    def summarize(self, analysis: List[List[Dict]]) -> Dict:
        patterns = {}
        for layer in analysis:
            for head in layer:
                p = head["pattern"]
                patterns[p] = patterns.get(p, 0) + 1
        return {
            "total_heads": sum(patterns.values()),
            "pattern_distribution": patterns,
            "avg_entropy": sum(h["entropy"] for l in analysis for h in l) / max(sum(len(l) for l in analysis), 1),
        }
