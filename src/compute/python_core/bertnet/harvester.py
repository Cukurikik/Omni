from typing import Set

class BertnetHarvester:
    def compute_jaccard(self, set_a: Set[str], set_b: Set[str]) -> float:
        if not set_a and not set_b:
            return 1.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersection / union if union > 0 else 0.0
