# Omni Knowledge Circuits Tracer (Python)
# Compute Layer: Circuit-level knowledge attribution in pretrained transformers.
# Ref: zjunlp/KnowledgeCircuits — NeurIPS 2024, Knowledge Circuits in Pretrained Transformers.

from typing import List, Dict, Tuple
import math

class CircuitNode:
    __slots__ = ('layer_idx', 'head_idx', 'attribution_score')
    def __init__(self, layer_idx: int, head_idx: int, attribution_score: float):
        self.layer_idx = layer_idx
        self.head_idx = head_idx
        self.attribution_score = attribution_score

def trace_knowledge_circuit(
    layer_activations: List[List[float]],
    threshold: float = 0.1
) -> List[CircuitNode]:
    if not layer_activations:
        return []
    circuit: List[CircuitNode] = []
    for layer_idx, heads in enumerate(layer_activations):
        for head_idx, activation in enumerate(heads):
            score = math.tanh(activation)
            if abs(score) >= threshold:
                circuit.append(CircuitNode(layer_idx, head_idx, round(score, 8)))
    circuit.sort(key=lambda n: abs(n.attribution_score), reverse=True)
    return circuit

def compute_circuit_importance(circuit: List[CircuitNode]) -> float:
    if not circuit:
        return 0.0
    total = sum(abs(n.attribution_score) for n in circuit)
    return round(total / len(circuit), 8)
