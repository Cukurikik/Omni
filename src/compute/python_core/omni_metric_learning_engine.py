"""
OMNI Metric Learning Engine
===========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
from typing import Dict, Any, Tuple

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class OmniMetricLearningEngine:
    """
    omni-metric-learning
    
    A zero-mock native engine simulating Deep Metric / Contrastive Learning architectures.
    Implements a strict Triplet Margin Loss algorithm computing forward distances 
    and backward gradient manifolds natively to cluster high-dimensional semantic spaces.
    """
    
    ENGINE_VERSION = "omni-s6-b8.1.0"
    
    def __init__(self, margin: float = 1.0):
        """Initialize OmniMetricLearningEngine."""
        self.margin = margin
        
    def _euclidean_distance(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Calculates element-wise L2 norm between vector batches."""
        # a, b shape: (batch, embed_dim)
        return np.sqrt(np.sum(np.square(a - b), axis=-1) + 1e-12)

    def compute_triplet_loss_and_gradients(self, anchor: np.ndarray, positive: np.ndarray, negative: np.ndarray) -> Result:
        """
        Native Triplet Margin Loss bounding.
        Loss = max(0, d(A, P) - d(A, N) + margin)
        Returns bounded loss value and the corresponding gradients w.r.t A, P, N.
        
        Args:
            anchor: (B, D) float array
            positive: (B, D) float array
            negative: (B, D) float array
        """
        try:
            B, D = anchor.shape
            
            # Forward Distances
            d_ap = self._euclidean_distance(anchor, positive) # (B,)
            d_an = self._euclidean_distance(anchor, negative) # (B,)
            
            # Loss mask where margin is violated
            losses = d_ap - d_an + self.margin
            mask = losses > 0
            
            # Mean loss
            total_loss = np.sum(losses[mask]) / max(1, B)
            
            # Backward Gradients
            # d_ap w.r.t anchor = (anchor - positive) / d_ap
            # d_an w.r.t anchor = (anchor - negative) / d_an
            
            grad_anchor = np.zeros_like(anchor)
            grad_positive = np.zeros_like(positive)
            grad_negative = np.zeros_like(negative)
            
            for i in range(B):
                if mask[i]:
                    # Gradients
                    grad_d_ap_a = (anchor[i] - positive[i]) / d_ap[i]
                    grad_d_an_a = (anchor[i] - negative[i]) / d_an[i]
                    
                    # dL/dA = d_ap_a - d_an_a
                    grad_anchor[i] = (grad_d_ap_a - grad_d_an_a) / B
                    
                    # dL/dP = - d_ap_a
                    grad_positive[i] = (-grad_d_ap_a) / B
                    
                    # dL/dN = d_an_a
                    grad_negative[i] = (grad_d_an_a) / B
                    
            return Result(value={
                "loss": float(total_loss),
                "grad_anchor": grad_anchor,
                "grad_positive": grad_positive,
                "grad_negative": grad_negative,
                "triplet_violations": int(np.sum(mask))
            })
            
        except Exception as e:
            return Result(error=f"Metric learning error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniMetricLearningEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "components": ["TripletMarginLoss", "NegativeMiningGradientMapping"]
        }
