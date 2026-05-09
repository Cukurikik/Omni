import typing
from typing import Dict, Any, List

class FederatedAggregatorEngine:
    """
    OMNI Framework - Federated Learning Aggregator
    Aggregates model weights from edge devices (e.g., FedAvg).
    """
    def __init__(self, global_model_shape: List[int]):
        self.global_model_shape = global_model_shape
        self.global_weights = [0.0] * sum(global_model_shape)

    def aggregate_updates(self, client_weights: List[List[float]], client_samples: List[int]) -> Dict[str, Any]:
        """Performs Federated Averaging on client updates."""
        if not client_weights or not client_samples:
            return {"status": "error", "error": "No updates to aggregate"}
            
        total_samples = sum(client_samples)
        if total_samples == 0:
            return {"status": "error", "error": "Zero total samples"}
            
        # OMNI FedAvg implementation mock
        new_weights = [0.0] * len(self.global_weights)
        for w_list, n in zip(client_weights, client_samples):
            weight_factor = n / total_samples
            for i, w in enumerate(w_list):
                if i < len(new_weights):
                    new_weights[i] += w * weight_factor
                    
        self.global_weights = new_weights
        
        return {
            "status": "success",
            "clients_aggregated": len(client_weights),
            "total_samples": total_samples,
            "updated_weight_sum": sum(self.global_weights)
        }
