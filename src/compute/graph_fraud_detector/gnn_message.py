class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class GraphMessageMath:
    def __init__(self):
        pass

    def compute_node_aggregation(self, node_feature: float, neighbor_features: list[float], weight: float) -> OmniResult:
        if not neighbor_features:
            return OmniResult(value=node_feature) # No neighbors

        # Deterministic simulation of GNN Message Passing / Graph Convolution
        # h_v^{(l+1)} = \sigma( W \cdot \sum_{u \in N(v)} h_u^{(l)} + B \cdot h_v^{(l)} )
        
        try:
            # Simple sum aggregation
            neighbor_sum = sum(neighbor_features)
            
            # Weighted update
            aggregated_feature = (node_feature + neighbor_sum) * weight
            
            # ReLU Activation
            output = max(0.0, aggregated_feature)
            
            return OmniResult(value=output)
        except Exception as e:
            return OmniResult(error=str(e))
