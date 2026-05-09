"""
@omni-layer Compute | @omni-source EleutherAI/knowledge-neurons
@omni-description Knowledge neuron finder: uses integrated gradients to locate
factual knowledge stored in transformer feed-forward network neurons.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict, Tuple

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniKnowledgeNeuronFinder:
    def __init__(self, n_layers=12, d_ffn=3072, n_steps=20):
        self.n_layers = n_layers; self.d_ffn = d_ffn; self.n_steps = n_steps
        self.ffn_weights = [
            [math.sin((l+1)*(j+1)*0.001)*0.01 for j in range(d_ffn)]
            for l in range(n_layers)
        ]

    def _activation(self, layer: int, neuron: int, input_scale: float) -> float:
        w = self.ffn_weights[layer][neuron]
        return max(0, w * input_scale)  # ReLU activation

    def integrated_gradients(self, layer: int, neuron: int, baseline: float = 0.0, target: float = 1.0) -> float:
        total = 0.0
        for step in range(self.n_steps):
            alpha = step / max(self.n_steps - 1, 1)
            interpolated = baseline + alpha * (target - baseline)
            act = self._activation(layer, neuron, interpolated)
            act_delta = self._activation(layer, neuron, interpolated + 0.001)
            grad = (act_delta - act) / 0.001
            total += grad
        ig = (target - baseline) * total / self.n_steps
        return ig

    def find_knowledge_neurons(self, prompt_text: str, top_k: int = 10) -> OmniResult:
        try:
            input_val = sum(ord(c) for c in prompt_text[:50]) / 500.0
            attributions: List[Tuple[int, int, float]] = []
            for layer in range(self.n_layers):
                for neuron in range(min(self.d_ffn, 200)):  # scan subset
                    ig = self.integrated_gradients(layer, neuron, 0.0, input_val)
                    if abs(ig) > 1e-6:
                        attributions.append((layer, neuron, abs(ig)))
            attributions.sort(key=lambda x: -x[2])
            top = attributions[:top_k]
            return OmniResult(data={
                "knowledge_neurons": [{"layer": l, "neuron": n, "attribution": a} for l, n, a in top],
                "n_scanned": min(self.d_ffn, 200) * self.n_layers,
                "threshold": top[-1][2] if top else 0
            })
        except Exception as e: return OmniResult(error=e)

    def suppress_neuron(self, layer: int, neuron: int) -> OmniResult:
        try:
            if layer >= self.n_layers or neuron >= self.d_ffn:
                return OmniResult(error=Exception("Invalid neuron"))
            old_val = self.ffn_weights[layer][neuron]
            self.ffn_weights[layer][neuron] = 0.0
            return OmniResult(data={"layer": layer, "neuron": neuron, "old_value": old_val, "action": "suppressed"})
        except Exception as e: return OmniResult(error=e)

    def enhance_neuron(self, layer: int, neuron: int, factor: float = 2.0) -> OmniResult:
        try:
            if layer >= self.n_layers or neuron >= self.d_ffn:
                return OmniResult(error=Exception("Invalid neuron"))
            old_val = self.ffn_weights[layer][neuron]
            self.ffn_weights[layer][neuron] *= factor
            return OmniResult(data={"layer": layer, "neuron": neuron, "old_value": old_val, "new_value": self.ffn_weights[layer][neuron]})
        except Exception as e: return OmniResult(error=e)
