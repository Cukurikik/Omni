import math

class MoExtendError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self):
        if not self.is_ok():
            raise self.error
        return self.value

# OMNI Engine: moextend
# Logic for extending new modality experts dynamically based on parameter bounds.
class MoExtendTuningEngine:
    def __init__(self, max_expert_saturation: float = 0.85):
        self.max_saturation = max_expert_saturation

    def evaluate_new_expert_necessity(self, current_expert_load: list[float], new_modality_complexity: float) -> Result:
        try:
            if new_modality_complexity < 0.0:
                 return Result(error=MoExtendError("Modality complexity matrix collapsed negatively"))
            
            if not current_expert_load:
                return Result(value={"spawn_new_expert": True, "reason": "Zero active experts in pipeline"})

            total_load = sum(current_expert_load)
            avg_load = total_load / len(current_expert_load)

            if avg_load < 0.0 or avg_load > 1.0:
                 return Result(error=MoExtendError("Expert load boundary historically broken"))

            # If existing experts are highly saturated OR the new modality is incredibly complex
            spawn_expert = (avg_load > self.max_saturation) or (new_modality_complexity > 0.9)

            return Result(value={
                "spawn_new_expert": spawn_expert,
                "projected_cost": new_modality_complexity * avg_load if spawn_expert else 0.0
            })

        except Exception as e:
            return Result(error=MoExtendError(f"MoExtend expert routing failed: {str(e)}"))
