import uuid
from typing import Dict, Any, List
from dataclasses import dataclass, field
import numpy as np

# OMNI Monadic Type
@dataclass
class Result:
    is_ok: bool
    value: Any = None
    error: str = None

    @classmethod
    def Ok(cls, value: Any):
        return cls(is_ok=True, value=value)

    @classmethod
    def Err(cls, error: str):
        return cls(is_ok=False, error=error)

def ok(value: Any) -> Result:
    return Result.Ok(value)

def err(error: str) -> Result:
    return Result.Err(error)

@dataclass
class OmniFederatedLearningEngine:
    """
    OmniFederatedLearningEngine
    Domain: Federated Learning (Distributed Secure Weights Aggregation)
    Mathematically constructs Byzantine-fault-tolerant gradient bounds via
    Krum aggregation, isolating malicious or highly variant nodes in a decentralized space.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    byzantine_node_tolerance: int = 1

    def _krum_aggregation_bounds(self, gradient_vectors: np.ndarray) -> np.ndarray:
        """
        Calculates geometric bounds isolating reliable gradients from chaotic nodes
        by scoring dense nearest-neighbors aggregations.
        gradient_vectors: (Num_Nodes, Num_Parameters)
        """
        num_nodes = gradient_vectors.shape[0]
        
        if num_nodes <= 2 * self.byzantine_node_tolerance + 2:
            # Fallback to mean if tolerance logic is mathematically unresolvable
            return np.mean(gradient_vectors, axis=0)
            
        distances = np.zeros((num_nodes, num_nodes))
        
        # Calculate pairwise Euclidean distances between node gradients
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:
                    distances[i, j] = np.linalg.norm(gradient_vectors[i] - gradient_vectors[j])
                    
        # Krum score: Sum of closest (num_nodes - byzantine_tolerance - 2) distances
        scores = np.zeros(num_nodes)
        k_closest = num_nodes - self.byzantine_node_tolerance - 2
        
        for i in range(num_nodes):
            # Sort distances excluding self
            sorted_dist = np.sort(distances[i])[1:] 
            scores[i] = np.sum(sorted_dist[:k_closest])
            
        # Select the node representing the most dense cluster center (lowest score)
        best_node_idx = np.argmin(scores)
        
        return gradient_vectors[best_node_idx]

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "node_gradient_updates" not in payload:
                return err("Missing decentralized gradient vectors for Federated Aggregation.")
                
            updates = np.array(payload["node_gradient_updates"], dtype=np.float32)

            if updates.ndim != 2:
                return err("Gradients must map 2D structures (Nodes, Parameters).")

            aggregated_gradient = self._krum_aggregation_bounds(updates)
            
            # Simple divergence metric: was the selected center far from the mean?
            mean_grad = np.mean(updates, axis=0)
            center_drift = float(np.linalg.norm(aggregated_gradient - mean_grad))

            return ok({
                "engine_id": self.engine_id,
                "global_aggregated_gradient_shape": list(aggregated_gradient.shape),
                "krum_center_drift": center_drift,
                "status": "Byzantine-Resilient Gradients Synthesized"
            })
            
        except Exception as e:
            return err(f"Federated Learning aggregation failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniFederatedLearningEngine",
            "status": "Operational",
            "byzantine_tolerance": self.byzantine_node_tolerance
        }
