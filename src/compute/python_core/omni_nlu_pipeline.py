"""
OMNI Compute — NLU Pipeline (OpenAutoNLU-inspired)
Automated NLU training: NER + classification + intent detection.
"""
import logging, json, time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("omni.nlu")

@dataclass
class NLUExample:
    text: str; intent: str = ""; entities: List[Dict] = field(default_factory=list)
    label: str = ""

@dataclass
class NLUConfig:
    task: str = "classification"  # classification | ner | intent
    model_name: str = "bert-base-uncased"; max_seq_len: int = 256
    num_labels: int = 2; learning_rate: float = 3e-5
    batch_size: int = 16; epochs: int = 5; dropout: float = 0.1

class OmniNLUPipeline:
    """Automated NLU pipeline for text classification, NER, intent detection."""
    def __init__(self, config: NLUConfig):
        self.config = config
        self.train_data: List[NLUExample] = []
        self.label_map: Dict[str, int] = {}
    def load_data(self, data: List[Dict]):
        for d in data:
            ex = NLUExample(text=d["text"], intent=d.get("intent",""),
                           entities=d.get("entities",[]), label=d.get("label",""))
            self.train_data.append(ex)
            if ex.label and ex.label not in self.label_map:
                self.label_map[ex.label] = len(self.label_map)
            if ex.intent and ex.intent not in self.label_map:
                self.label_map[ex.intent] = len(self.label_map)
        logger.info(f"Loaded {len(self.train_data)} examples, {len(self.label_map)} labels")
    def preprocess(self) -> List[Dict]:
        processed = []
        for ex in self.train_data:
            text = ex.text.strip().lower()
            label_id = self.label_map.get(ex.label or ex.intent, 0)
            processed.append({"text": text, "label_id": label_id, "original": ex})
        return processed
    def compute_class_weights(self) -> Dict[int, float]:
        counts: Dict[int, int] = {}
        for ex in self.train_data:
            lid = self.label_map.get(ex.label or ex.intent, 0)
            counts[lid] = counts.get(lid, 0) + 1
        total = sum(counts.values())
        return {k: total / (len(counts) * v) for k, v in counts.items()}
    def evaluate(self, predictions: List[int], gold: List[int]) -> Dict:
        correct = sum(1 for p, g in zip(predictions, gold) if p == g)
        acc = correct / max(len(predictions), 1)
        # Per-class metrics
        classes = set(gold)
        per_class = {}
        for c in classes:
            tp = sum(1 for p, g in zip(predictions, gold) if p == c and g == c)
            fp = sum(1 for p, g in zip(predictions, gold) if p == c and g != c)
            fn = sum(1 for p, g in zip(predictions, gold) if p != c and g == c)
            prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
            f1 = 2 * prec * rec / max(prec + rec, 1e-8)
            per_class[c] = {"precision": prec, "recall": rec, "f1": f1}
        macro_f1 = sum(m["f1"] for m in per_class.values()) / max(len(per_class), 1)
        return {"accuracy": acc, "macro_f1": macro_f1, "per_class": per_class}
    def get_summary(self) -> Dict:
        return {"task": self.config.task, "model": self.config.model_name,
                "num_examples": len(self.train_data), "num_labels": len(self.label_map),
                "labels": self.label_map}
