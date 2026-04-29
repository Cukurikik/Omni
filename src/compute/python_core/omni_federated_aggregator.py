# Omni Federated Aggregator Engine
from typing import List, Dict

def fedavg_aggregation(client_weights: List[List[float]], client_data_sizes: List[int]) -> List[float]:
    """Execute Federated Averaging (FedAvg) across client model weights."""
    if not client_weights or not client_data_sizes or len(client_weights) != len(client_data_sizes):
        return []
        
    total_data = sum(client_data_sizes)
    if total_data == 0:
        return []
        
    num_params = len(client_weights[0])
    aggregated = [0.0] * num_params
    
    for weights, size in zip(client_weights, client_data_sizes):
        weight_factor = size / total_data
        for i in range(num_params):
            aggregated[i] += weights[i] * weight_factor
            
    return [round(w, 6) for w in aggregated]

def calculate_client_divergence(global_weights: List[float], client_weights: List[float]) -> float:
    """Calculate L2 divergence of client weights from the global model."""
    if len(global_weights) != len(client_weights):
        return 0.0
        
    l2_sum = sum((g - c)**2 for g, c in zip(global_weights, client_weights))
    return round(l2_sum ** 0.5, 6)
