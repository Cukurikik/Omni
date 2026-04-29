# Omni InfiGUI-G1 AEPO Agent
# Compute Layer: Adaptive Exploration Policy Optimization for GUI agents.
# Ref: InfiXAI/InfiGUI-G1 — AAAI 2026 Oral
# Key: Guided exploration overcomes semantic alignment bottlenecks.
import math, hashlib
from typing import List, Dict, Tuple, Optional

def compute_gui_action_reward(predicted_bbox: Tuple[float,float,float,float],
                               ground_truth_bbox: Tuple[float,float,float,float]) -> float:
    x1 = max(predicted_bbox[0], ground_truth_bbox[0])
    y1 = max(predicted_bbox[1], ground_truth_bbox[1])
    x2 = min(predicted_bbox[2], ground_truth_bbox[2])
    y2 = min(predicted_bbox[3], ground_truth_bbox[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_p = (predicted_bbox[2] - predicted_bbox[0]) * (predicted_bbox[3] - predicted_bbox[1])
    area_g = (ground_truth_bbox[2] - ground_truth_bbox[0]) * (ground_truth_bbox[3] - ground_truth_bbox[1])
    union = area_p + area_g - inter
    return inter / union if union > 0 else 0.0

def aepo_exploration_score(action_history: List[Dict], current_state_hash: str) -> float:
    visited = set()
    for act in action_history:
        visited.add(act.get("state_hash", ""))
    novelty = 0.0 if current_state_hash in visited else 1.0
    diversity = len(visited) / max(len(action_history), 1)
    return 0.6 * novelty + 0.4 * diversity

def select_gui_action(actions: List[Dict], exploration_weight: float = 0.3) -> Dict:
    if not actions:
        return {"status": "error", "message": "OMNI_ERR: No actions available"}
    best = max(actions, key=lambda a: a.get("q_value", 0.0) * (1 - exploration_weight) + a.get("exploration", 0.0) * exploration_weight)
    return {"status": "ok", "selected_action": best}

def grounding_accuracy(predictions: List[Tuple], ground_truths: List[Tuple], iou_threshold: float = 0.5) -> float:
    if not predictions or not ground_truths:
        return 0.0
    correct = sum(1 for p, g in zip(predictions, ground_truths) if compute_gui_action_reward(p, g) >= iou_threshold)
    return correct / len(ground_truths)
