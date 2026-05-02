"""
@omni-domain Compute Layer (Fact Verification)
@omni-source GAIR-NLP/factool
@omni-description Factool Detector mimicking claim verification pipeline.
@omni-requirement zero-mock, monadic-error
"""
from typing import Any, Optional, List, Dict

class OmniResult:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error
    def is_ok(self): return self.error is None

class FactoolError(Exception): pass

class FactoolDetector:
    def __init__(self, similarity_threshold=0.7):
        self.similarity_threshold = similarity_threshold
        self.knowledge_base = {}

    def add_evidence(self, topic: str, facts: List[str]) -> OmniResult:
        try:
            if not topic:
                return OmniResult(error=FactoolError("Topic cannot be empty."))
            self.knowledge_base[topic.lower()] = facts
            return OmniResult(data=True)
        except Exception as e:
            return OmniResult(error=FactoolError(f"Evidence addition failed: {e}"))

    def extract_claims(self, text: str) -> OmniResult:
        try:
            if not text:
                return OmniResult(error=FactoolError("Text cannot be empty."))
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            claims = [{"text": s, "id": i} for i, s in enumerate(sentences)]
            return OmniResult(data={"claims": claims})
        except Exception as e:
            return OmniResult(error=FactoolError(f"Claim extraction failed: {e}"))

    def _jaccard_similarity(self, s1: str, s2: str) -> float:
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())
        if not set1 or not set2:
            return 0.0
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union)

    def verify_claim(self, claim: str) -> OmniResult:
        try:
            if not claim:
                return OmniResult(error=FactoolError("Claim is empty."))
            best_score = 0.0
            best_match = None
            for topic, facts in self.knowledge_base.items():
                for fact in facts:
                    score = self._jaccard_similarity(claim, fact)
                    if score > best_score:
                        best_score = score
                        best_match = fact
            verdict = "SUPPORTED" if best_score >= self.similarity_threshold else "NOT_SUPPORTED"
            return OmniResult(data={"claim": claim, "verdict": verdict, "confidence": best_score, "evidence": best_match})
        except Exception as e:
            return OmniResult(error=FactoolError(f"Verification failed: {e}"))

    def verify_document(self, text: str) -> OmniResult:
        try:
            claims_result = self.extract_claims(text)
            if not claims_result.is_ok():
                return claims_result
            results = []
            for claim in claims_result.data["claims"]:
                v = self.verify_claim(claim["text"])
                if v.is_ok():
                    results.append(v.data)
            supported = sum(1 for r in results if r["verdict"] == "SUPPORTED")
            return OmniResult(data={"results": results, "supported_ratio": supported / max(len(results), 1)})
        except Exception as e:
            return OmniResult(error=FactoolError(f"Document verification failed: {e}"))
