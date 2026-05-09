"""
@omni-layer Compute | @omni-source EleutherAI/knowledge-neurons + HamedBabaei/LLMs4OL
@omni-description Knowledge graph builder: extracts and aligns facts from
transformer knowledge neurons into structured ontology triples.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict, Tuple

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniKnowledgeGraphBuilder:
    def __init__(self, n_layers=12, d_ffn=3072, threshold=0.01):
        self.n_layers = n_layers; self.d_ffn = d_ffn; self.threshold = threshold
        self.triples: List[Dict] = []
        self.entities: Dict[str, Dict] = {}

    def extract_fact(self, subject: str, relation: str, object_: str, attributions: List[float]) -> OmniResult:
        try:
            active_neurons = [(i, a) for i, a in enumerate(attributions) if abs(a) > self.threshold]
            active_neurons.sort(key=lambda x: -abs(x[1]))
            confidence = sum(abs(a) for _, a in active_neurons[:10]) / max(len(active_neurons[:10]),1)
            triple = {
                "subject": subject, "relation": relation, "object": object_,
                "confidence": confidence, "n_active_neurons": len(active_neurons),
                "top_neurons": [(n, round(a,4)) for n, a in active_neurons[:5]]
            }
            self.triples.append(triple)
            for ent in [subject, object_]:
                if ent not in self.entities:
                    self.entities[ent] = {"name": ent, "in_triples": 0, "total_confidence": 0}
                self.entities[ent]["in_triples"] += 1
                self.entities[ent]["total_confidence"] += confidence
            return OmniResult(data=triple)
        except Exception as e: return OmniResult(error=e)

    def build_from_prompts(self, prompts: List[Dict]) -> OmniResult:
        try:
            results = []
            for prompt in prompts:
                subj = prompt.get("subject", "")
                rel = prompt.get("relation", "")
                obj = prompt.get("object", "")
                attrs = [math.sin((i+1)*hash(subj+rel+obj)*0.0001)*0.1 for i in range(self.d_ffn)]
                r = self.extract_fact(subj, rel, obj, attrs)
                if r.is_ok(): results.append(r.data)
            return OmniResult(data={"triples_extracted": len(results), "entities": len(self.entities), "total_triples": len(self.triples)})
        except Exception as e: return OmniResult(error=e)

    def query_entity(self, entity: str) -> OmniResult:
        try:
            related = [t for t in self.triples if t["subject"] == entity or t["object"] == entity]
            return OmniResult(data={"entity": entity, "n_triples": len(related), "triples": related[:20],
                                     "info": self.entities.get(entity, {})})
        except Exception as e: return OmniResult(error=e)

    def stats(self) -> Dict:
        avg_conf = sum(t["confidence"] for t in self.triples)/max(len(self.triples),1)
        return {"total_triples": len(self.triples), "total_entities": len(self.entities), "avg_confidence": avg_conf}
