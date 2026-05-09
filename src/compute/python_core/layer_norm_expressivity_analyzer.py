import typing
from typing import Dict, Any, List
import math

class LayerNormExpressivityAnalyzer:
    """
    OMNI Framework - LayerNorm Expressivity Analyzer
    Analyzes the expressivity role of LayerNorm in Transformers' Attention.
    """
    def __init__(self, hidden_dim: int, eps: float = 1e-5):
        self.hidden_dim = hidden_dim
        self.eps = eps
        self.weights: List[float] = [1.0] * hidden_dim
        self.bias: List[float] = [0.0] * hidden_dim

    def compute_expressivity_score(self, activation_variance: float) -> Dict[str, Any]:
        """Computes the expressivity score based on variance."""
        if activation_variance < 0:
            return {"status": "error", "error": "Variance cannot be negative"}
            
        # OMNI Compute logic for LayerNorm bound analysis
        score = math.sqrt(activation_variance + self.eps) * sum(self.weights) / self.hidden_dim
        
        return {
            "status": "success",
            "expressivity_score": score,
            "gradient_norm_projection": score * 0.1
        }

    def simulate_attention_shift(self, input_vector: List[float]) -> Dict[str, Any]:
        """Simulates how LayerNorm shifts attention distributions."""
        if len(input_vector) != self.hidden_dim:
            return {"status": "error", "error": f"Expected dim {self.hidden_dim}"}
            
        mean = sum(input_vector) / self.hidden_dim
        var = sum((x - mean) ** 2 for x in input_vector) / self.hidden_dim
        
        shifted = [((x - mean) / math.sqrt(var + self.eps)) * w + b 
                   for x, w, b in zip(input_vector, self.weights, self.bias)]
                   
        return {"status": "success", "shifted_vector": shifted}
