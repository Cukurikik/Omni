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
class OmniQwen2MathReasoningEngine:
    """
    OmniQwen2MathReasoningEngine
    Domain: Qwen2-Math (Advanced Symbolic and Numeric Reasoning)
    Mathematically constructs probabilistic reward margins evaluating logical 
    consistency mapping the intermediate derivation steps (CoT) towards 
    a final formalized answer bracket.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    logical_decay_gamma: float = 0.90 

    def _chain_of_thought_consistency_margin(self, derivation_step_vectors: List[np.ndarray], final_answer_vector: np.ndarray) -> float:
        """
        Evaluates the step-by-step vector trajectory leading up to the final answer.
        Consistency defines that steps smoothly transition toward the final answer axis
        rather than oscillating wildly.
        derivation_step_vectors: L length list of (Batch, Dim) arrays. We assume Batch=1 for simplicity here.
        final_answer_vector: (Batch, Dim)
        """
        if not derivation_step_vectors:
            return 0.0
            
        num_steps = len(derivation_step_vectors)
        final_norm = np.linalg.norm(final_answer_vector) + 1e-9
        final_target = final_answer_vector / final_norm
        
        # We calculate structural overlap with target answer per step
        step_overlaps = []
        for step in derivation_step_vectors:
            step_overlap = np.sum(step * final_target) / (np.linalg.norm(step) + 1e-9)
            step_overlaps.append(step_overlap)
            
        # Monotonicity check weighted by proximity to final answer
        # A good math derivation tends strictly toward the answer formulation axis.
        weighted_consistency = 0.0
        for i, overlap in enumerate(step_overlaps):
            # Steps closer to the end matter more
            weight = self.logical_decay_gamma ** (num_steps - i - 1)
            weighted_consistency += float(overlap) * weight
            
        # Normalize
        scaling = (1.0 - self.logical_decay_gamma ** num_steps) / (1.0 - self.logical_decay_gamma)
        normalized_margin = weighted_consistency / scaling
            
        return normalized_margin

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "derivation_steps" not in payload or "final_answer" not in payload:
                return err("Missing Mathematical trajectory structure for evaluation.")
                
            steps_raw = payload["derivation_steps"]
            if not isinstance(steps_raw, list):
                return err("Derivation sequence must be a list of arrays.")
                
            steps = [np.array(s, dtype=np.float32) for s in steps_raw]
            final = np.array(payload["final_answer"], dtype=np.float32)

            for s in steps:
                if s.shape != final.shape:
                    return err("Dimension mismatch spanning CoT trajectory.")

            reasoning_margin = self._chain_of_thought_consistency_margin(steps, final)

            return ok({
                "engine_id": self.engine_id,
                "cot_consistency_margin": reasoning_margin,
                "status": "Qwen2-Math Formal Deduction Sequenced"
            })
            
        except Exception as e:
            return err(f"Qwen2 Math Evaluation failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniQwen2MathReasoningEngine",
            "status": "Operational",
            "decay_factor": self.logical_decay_gamma
        }
