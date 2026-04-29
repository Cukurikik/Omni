class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class FedAvgMath:
    def __init__(self):
        pass

    def compute_weighted_average(self, client_weights: list[list[float]], data_samples: list[int]) -> OmniResult:
        if not client_weights or not data_samples or len(client_weights) != len(data_samples):
            return OmniResult(error="Invalid client arrays for FedAvg calculation")

        total_samples = sum(data_samples)
        if total_samples == 0:
            return OmniResult(error="Total samples must be > 0")

        num_params = len(client_weights[0])
        global_weights = [0.0] * num_params

        # Deterministic mathematical calculation of Federated Averaging (FedAvg)
        # w_global = sum( (n_k / n_total) * w_k )
        
        for k in range(len(client_weights)):
            weight_fraction = data_samples[k] / float(total_samples)
            
            for i in range(num_params):
                global_weights[i] += client_weights[k][i] * weight_fraction

        return OmniResult(value={
            "global_weights": global_weights,
            "total_clients_aggregated": len(client_weights)
        })
