import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class StdpPlasticity:
    def __init__(self):
        pass

    def compute_weight_update(self, pre_synaptic_time_ms: float, post_synaptic_time_ms: float) -> OmniResult:
        # Deterministic calculation of Spike-Timing-Dependent Plasticity (STDP).
        # This is the fundamental biological rule of learning: "Neurons that fire together, wire together."
        # If the pre-synaptic neuron fires JUST BEFORE the post-synaptic neuron, the connection strengthens.
        # If it fires AFTER, the connection weakens (anti-causal).
        try:
            delta_t = post_synaptic_time_ms - pre_synaptic_time_ms
            
            # STDP Exponential Window Parameters
            A_plus = 0.01  # Max learning rate (potentiation)
            A_minus = -0.0105 # Max forgetting rate (depression, usually slightly stronger)
            tau_plus = 20.0 # Time constant (ms)
            tau_minus = 20.0
            
            weight_delta = 0.0
            
            if delta_t > 0:
                # Pre fires before Post -> Causality -> Strengthen Synapse (LTP)
                weight_delta = A_plus * math.exp(-delta_t / tau_plus)
            elif delta_t < 0:
                # Pre fires after Post -> Anti-causal -> Weaken Synapse (LTD)
                weight_delta = A_minus * math.exp(delta_t / tau_minus)
                
            return OmniResult(value=weight_delta)
        except Exception as e:
            return OmniResult(error=str(e))
