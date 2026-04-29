# Omni Knowledge Circuits Engine
# Ref: zjunlp/KnowledgeCircuits
from typing import List, Dict
import math

def calculate_attention_head_importance(attention_weights: List[List[float]], target_idx: int) -> float:
    """Calculate the importance of an attention head for a specific token index."""
    if not attention_weights or target_idx >= len(attention_weights):
        return 0.0
    
    # Sum of attention directed to the target token
    importance = sum(row[target_idx] for row in attention_weights)
    return round(importance / max(len(attention_weights), 1), 6)

def locate_knowledge_circuit(layer_attentions: Dict[int, List[List[float]]], target_idx: int, top_k: int = 3) -> List[int]:
    """Identify the top-k layers forming a knowledge circuit for a target entity."""
    scored_layers = []
    for layer_id, weights in layer_attentions.items():
        score = calculate_attention_head_importance(weights, target_idx)
        scored_layers.append((layer_id, score))
        
    scored_layers.sort(key=lambda x: x[1], reverse=True)
    return [layer for layer, score in scored_layers[:top_k]]

def compute_circuit_overlap(circuit_a: List[int], circuit_b: List[int]) -> float:
    """Calculate overlap between two knowledge circuits."""
    if not circuit_a or not circuit_b:
        return 0.0
    intersection = len(set(circuit_a) & set(circuit_b))
    union = len(set(circuit_a) | set(circuit_b))
    return round(intersection / max(union, 1), 4)
