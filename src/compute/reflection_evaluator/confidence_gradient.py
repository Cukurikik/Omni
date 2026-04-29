class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ConfidenceGradient:
    def __init__(self):
        pass

    def evaluate_reflection_improvement(self, initial_confidence: float, refined_confidence: float) -> OmniResult:
        if initial_confidence < 0.0 or refined_confidence < 0.0:
            return OmniResult(error="Confidence scores must be non-negative")

        # Deterministic simulation of Self-Reflection gradients
        # Used by Reflection agents to judge if their self-critique actually improved the answer
        try:
            gradient = refined_confidence - initial_confidence
            
            # Did the agent actually improve its certainty?
            if gradient > 0.05:
                return OmniResult(value={"improved": True, "gradient": gradient})
            else:
                return OmniResult(value={"improved": False, "gradient": gradient})
                
        except Exception as e:
            return OmniResult(error=str(e))
