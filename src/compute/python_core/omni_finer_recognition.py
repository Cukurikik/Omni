# Omni FineR Visual Recognition Engine
# Ref: OatmealLiu/FineR — ICLR'24, Apache-2.0
from typing import List, Dict
def attribute_extraction(image_desc: str, attributes: List[str]) -> Dict:
    desc_lower = image_desc.lower()
    found = {a: a.lower() in desc_lower for a in attributes}
    return {"attributes": found, "n_found": sum(found.values())}
def hierarchical_classify(predictions: List[str], taxonomy: Dict) -> str:
    for pred in predictions:
        for parent, children in taxonomy.items():
            if pred in children: return f"{parent}/{pred}"
    return predictions[0] if predictions else "unknown"
def finer_accuracy(preds: List[str], golds: List[str]) -> Dict:
    correct = sum(1 for p,g in zip(preds,golds) if p.strip().lower()==g.strip().lower())
    return {"accuracy": round(correct/max(len(golds),1),4)}
