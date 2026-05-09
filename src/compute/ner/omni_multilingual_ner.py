"""
@omni-layer Compute | @omni-source savasy/Turkish-Bert-NLP-Pipeline
@omni-description Multilingual NER engine: BERT-based named entity recognition
with BIO tagging and entity linking for Turkish and other languages.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

NER_TAGS = ["O","B-PER","I-PER","B-ORG","I-ORG","B-LOC","I-LOC","B-MISC","I-MISC"]

class OmniMultilingualNER:
    def __init__(self, d=768, n_tags=9):
        self.d = d; self.n_tags = n_tags
        self.crf_transitions = [[math.sin((i+1)*(j+1)*0.1)*0.5 for j in range(n_tags)] for i in range(n_tags)]

    def tag_sequence(self, embeddings: List[List[float]]) -> OmniResult:
        try:
            if not embeddings: return OmniResult(error=Exception("Empty"))
            emissions = []
            for emb in embeddings:
                scores = [sum(emb[j]*math.sin((t+1)*(j+1)*0.003)*0.02 for j in range(min(len(emb),32))) for t in range(self.n_tags)]
                emissions.append(scores)
            # Viterbi decode
            n = len(emissions)
            dp = [list(emissions[0])]
            backptr = []
            for t in range(1, n):
                new_dp = []; bp = []
                for j in range(self.n_tags):
                    candidates = [dp[t-1][i] + self.crf_transitions[i][j] + emissions[t][j] for i in range(self.n_tags)]
                    best = max(range(self.n_tags), key=lambda i: candidates[i])
                    new_dp.append(candidates[best])
                    bp.append(best)
                dp.append(new_dp); backptr.append(bp)
            tags = [max(range(self.n_tags), key=lambda i: dp[-1][i])]
            for t in range(len(backptr)-1, -1, -1):
                tags.append(backptr[t][tags[-1]])
            tags.reverse()
            entities = self._extract_entities(tags)
            return OmniResult(data={"tags": [NER_TAGS[t] for t in tags], "entities": entities, "n_tokens": n})
        except Exception as e: return OmniResult(error=e)

    def _extract_entities(self, tag_ids: List[int]) -> List[Dict]:
        entities = []; current = None
        for i, tid in enumerate(tag_ids):
            tag = NER_TAGS[tid]
            if tag.startswith("B-"):
                if current: entities.append(current)
                current = {"type": tag[2:], "start": i, "end": i+1}
            elif tag.startswith("I-") and current and current["type"] == tag[2:]:
                current["end"] = i+1
            else:
                if current: entities.append(current); current = None
        if current: entities.append(current)
        return entities
