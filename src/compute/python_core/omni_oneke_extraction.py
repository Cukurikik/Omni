# Omni OneKE Knowledge Extraction Engine
# Ref: zjunlp/OneKE — WWW'25 | MIT
from typing import List, Dict
import re

def extract_entities(text: str, schema: List[str]) -> List[Dict]:
    results = []
    for etype in schema:
        pattern = rf'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        for m in re.finditer(pattern, text):
            results.append({"text": m.group(), "type": etype, "start": m.start(), "end": m.end()})
    return results

def extract_relations(text: str, entities: List[Dict], rel_schema: List[str]) -> List[Dict]:
    rels = []
    for i, e1 in enumerate(entities):
        for j, e2 in enumerate(entities):
            if i >= j: continue
            dist = abs(e1["start"] - e2["start"])
            if dist < 200:
                rels.append({"head": e1["text"], "tail": e2["text"], "relation": rel_schema[0] if rel_schema else "related", "confidence": round(1.0/(1+dist/100), 4)})
    return rels

def ner_f1(pred: List[Dict], gold: List[Dict]) -> Dict:
    pred_set = {(e["text"], e["type"]) for e in pred}
    gold_set = {(e["text"], e["type"]) for e in gold}
    tp = len(pred_set & gold_set); p = tp/max(len(pred_set),1); r = tp/max(len(gold_set),1)
    f1 = 2*p*r/max(p+r, 1e-8)
    return {"precision": round(p,4), "recall": round(r,4), "f1": round(f1,4)}
