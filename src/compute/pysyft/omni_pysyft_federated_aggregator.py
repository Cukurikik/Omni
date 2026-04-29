# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# PySyft Federated Aggregator (OMNI Zero-Mock Implementation)
# Implements FedAvg (Federated Averaging) for decentralized model synchronization.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[List[float]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class FederatedAveraging:
    def aggregate(self, client_weights: List[List[float]], client_data_sizes: List[int]) -> Result:
        if not client_weights or not client_data_sizes:
            return Result.err("Missing client inputs.")
        if len(client_weights) != len(client_data_sizes):
            return Result.err("Mismatch between weight arrays and client counts.")
            
        dim = len(client_weights[0])
        total_data = sum(client_data_sizes)
        
        if total_data == 0:
            return Result.err("Total data size across all clients is zero.")
            
        global_weights = [0.0] * dim
        
        for weights, data_size in zip(client_weights, client_data_sizes):
            if len(weights) != dim:
                return Result.err("Dimensional mismatch across client weights.")
                
            weight_factor = data_size / total_data
            for i in range(dim):
                global_weights[i] += weights[i] * weight_factor
                
        return Result.ok(global_weights)
