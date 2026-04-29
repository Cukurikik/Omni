# Omni InstructERC Emotion Classifier (Python)
# Compute Layer: Instruction-tuned emotion recognition in conversation.
# Ref: LIN-SHANG/InstructERC — ERC with LLM instruction tuning.

from typing import List, Dict
import math

EMOTIONS = ['happy', 'sad', 'angry', 'neutral', 'surprise', 'fear', 'disgust']

def classify_emotion(logits: List[float]) -> Dict[str, float]:
    if len(logits) != len(EMOTIONS): return {'error': 'DIMENSION_MISMATCH'}
    exp_l = [math.exp(l) for l in logits]
    total = sum(exp_l)
    return {e: round(v / total, 6) for e, v in zip(EMOTIONS, exp_l)}

def weighted_f1(predictions: List[str], gold: List[str]) -> float:
    if not gold or len(predictions) != len(gold): return 0.0
    labels = set(gold)
    f1_sum = 0.0
    weight_sum = 0
    for label in labels:
        tp = sum(1 for p, g in zip(predictions, gold) if p == g == label)
        fp = sum(1 for p, g in zip(predictions, gold) if p == label and g != label)
        fn = sum(1 for p, g in zip(predictions, gold) if p != label and g == label)
        prec = tp / (tp + fp) if tp + fp > 0 else 0
        rec = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec > 0 else 0
        count = sum(1 for g in gold if g == label)
        f1_sum += f1 * count
        weight_sum += count
    return round(f1_sum / weight_sum, 6) if weight_sum > 0 else 0.0
