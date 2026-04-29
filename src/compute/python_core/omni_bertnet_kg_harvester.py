# Omni BertNet KG Harvester
# Ref: tanyuqian/knowledge-harvest-from-lms — ACL 2023 Findings
# Implements: Knowledge graph extraction from PLMs via prompt mining
from typing import List, Dict, Tuple

def generate_relation_prompts(head: str, relation: str) -> List[str]:
    templates = [f"{head} is a type of [MASK]", f"{head} is related to [MASK]",
                 f"The {relation} of {head} is [MASK]", f"{head} has [MASK] as {relation}"]
    return templates

def extract_triples(head: str, predictions: List[Tuple[str, float]],
                     relation: str, threshold: float = 0.1) -> List[Dict]:
    triples = []
    for tail, conf in predictions:
        if conf >= threshold:
            triples.append({"head": head, "relation": relation, "tail": tail,
                           "confidence": round(conf, 6)})
    return triples

def merge_knowledge_graph(graphs: List[List[Dict]]) -> List[Dict]:
    seen = set(); merged = []
    for g in graphs:
        for triple in g:
            key = (triple["head"], triple["relation"], triple["tail"])
            if key not in seen: seen.add(key); merged.append(triple)
    return merged

def graph_quality_score(triples: List[Dict]) -> Dict:
    if not triples: return {"precision": 0, "coverage": 0}
    avg_conf = sum(t["confidence"] for t in triples) / len(triples)
    return {"n_triples": len(triples), "avg_confidence": round(avg_conf, 4),
            "unique_entities": len(set(t["head"] for t in triples) | set(t["tail"] for t in triples))}
