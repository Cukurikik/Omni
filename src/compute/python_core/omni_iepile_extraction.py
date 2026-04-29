# Omni IEPile Information Extraction Engine
# Ref: zjunlp/IEPile — ACL 2024
# Implements: Schema-based NER, RE, EE extraction with instruction generation
from typing import List, Dict

def build_ner_instruction(text: str, entity_types: List[str]) -> Dict:
    return {"task": "NER", "schema": entity_types, "input": text,
            "instruction": f"Extract entities of types {entity_types} from: {text}"}

def build_re_instruction(text: str, relation_types: List[str]) -> Dict:
    return {"task": "RE", "schema": relation_types, "input": text,
            "instruction": f"Extract relations of types {relation_types} from: {text}"}

def build_ee_instruction(text: str, event_types: List[str]) -> Dict:
    return {"task": "EE", "schema": event_types, "input": text,
            "instruction": f"Extract events of types {event_types} from: {text}"}

def hard_negative_sampling(schema: List[str], positive: List[str], n_neg: int = 3) -> List[str]:
    negatives = [s for s in schema if s not in positive]
    return negatives[:n_neg]

def evaluate_ie(predictions: List[Dict], ground_truth: List[Dict]) -> Dict:
    tp = fp = fn = 0
    for pred, gt in zip(predictions, ground_truth):
        pred_set = set(str(e) for e in pred.get("entities", []))
        gt_set = set(str(e) for e in gt.get("entities", []))
        tp += len(pred_set & gt_set); fp += len(pred_set - gt_set); fn += len(gt_set - pred_set)
    precision = tp / max(tp + fp, 1); recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
