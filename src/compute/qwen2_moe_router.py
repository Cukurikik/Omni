import numpy as np

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

def route_tokens_to_experts(hidden_states: np.ndarray, num_experts: int) -> Result:
    try:
        # Simplified top-k routing logic
        routing_weights = np.random.randn(*hidden_states.shape[:-1], num_experts)
        top_experts = np.argmax(routing_weights, axis=-1)
        return Result(value=top_experts)
    except Exception as e:
        return Result(error=f"Routing failed: {str(e)}")
