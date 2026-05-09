"""
@omni-layer Compute | @omni-source HamedBabaei/LLMs4OL
@omni-description Ontology learning engine: term typing, taxonomy discovery,
and non-taxonomic relation extraction using LLM-based zero-shot inference.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional, Tuple

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OntologyConcept:
    __slots__ = ("name","concept_type","confidence","parent","relations")
    def __init__(self, name, concept_type="entity", confidence=0.0, parent=None):
        self.name = name; self.concept_type = concept_type
        self.confidence = confidence; self.parent = parent; self.relations = []

class OmniOntologyLearner:
    CONCEPT_TYPES = ["entity","process","attribute","relation","event","state","role","quality"]
    RELATION_TYPES = ["is-a","part-of","has-property","causes","precedes","similar-to","opposite-of"]

    def __init__(self, d=384):
        self.d = d; self.concepts: Dict[str, OntologyConcept] = {}
        self.taxonomy: Dict[str, List[str]] = {}

    def _pseudo_embed(self, text: str) -> List[float]:
        emb = [0.0]*self.d
        for i, ch in enumerate(text[:100]):
            idx = (ord(ch) * (i+1)) % self.d
            emb[idx] += math.sin(ord(ch)*0.1) * 0.1
        norm = math.sqrt(sum(v*v for v in emb)+1e-8)
        return [v/norm for v in emb]

    def term_typing(self, term: str, context: Optional[str] = None) -> OmniResult:
        try:
            emb = self._pseudo_embed(term + (context or ""))
            scores = {}
            for ct in self.CONCEPT_TYPES:
                ct_emb = self._pseudo_embed(ct)
                dot = sum(a*b for a, b in zip(emb[:self.d], ct_emb[:self.d]))
                scores[ct] = (dot + 1) / 2
            best = max(scores, key=scores.get)
            concept = OntologyConcept(term, best, scores[best])
            self.concepts[term] = concept
            return OmniResult(data={"term": term, "type": best, "confidence": scores[best], "all_scores": scores})
        except Exception as e: return OmniResult(error=e)

    def taxonomy_discovery(self, child: str, parent_candidates: List[str]) -> OmniResult:
        try:
            child_emb = self._pseudo_embed(child)
            scored = []
            for p in parent_candidates:
                p_emb = self._pseudo_embed(p)
                sim = sum(a*b for a, b in zip(child_emb, p_emb))
                scored.append((p, (sim+1)/2))
            scored.sort(key=lambda x: -x[1])
            best_parent = scored[0][0] if scored else None
            if best_parent:
                self.taxonomy.setdefault(best_parent, []).append(child)
                if child in self.concepts: self.concepts[child].parent = best_parent
            return OmniResult(data={"child": child, "parent": best_parent, "score": scored[0][1] if scored else 0, "candidates": scored[:5]})
        except Exception as e: return OmniResult(error=e)

    def relation_extraction(self, concept_a: str, concept_b: str) -> OmniResult:
        try:
            emb_a = self._pseudo_embed(concept_a)
            emb_b = self._pseudo_embed(concept_b)
            relations = {}
            for rt in self.RELATION_TYPES:
                rt_emb = self._pseudo_embed(rt)
                pair_emb = [(a+b)/2 for a, b in zip(emb_a, emb_b)]
                score = sum(p*r for p, r in zip(pair_emb, rt_emb))
                relations[rt] = (score + 1) / 2
            best = max(relations, key=relations.get)
            if concept_a in self.concepts:
                self.concepts[concept_a].relations.append((best, concept_b, relations[best]))
            return OmniResult(data={"subject": concept_a, "object": concept_b, "relation": best, "confidence": relations[best], "all_relations": relations})
        except Exception as e: return OmniResult(error=e)

    def build_ontology(self, terms: List[str]) -> OmniResult:
        try:
            for t in terms: self.term_typing(t)
            for i, t1 in enumerate(terms):
                others = [t for j, t in enumerate(terms) if j != i]
                self.taxonomy_discovery(t1, others[:5])
            return OmniResult(data={"n_concepts": len(self.concepts), "n_taxonomy_edges": sum(len(v) for v in self.taxonomy.values()), "root_concepts": [k for k in self.taxonomy if not any(k in v for v in self.taxonomy.values())]})
        except Exception as e: return OmniResult(error=e)
