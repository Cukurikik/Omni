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
class OmniInstItPromptEngine:
    """
    OmniInstItPromptEngine
    Domain: Multimodal Instance Understanding (Inst-IT)
    Mathematically constructs visual prompt instruction bounds to boost 
    fine-grained localized understanding in Large Multimodal Models (LMMs).
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt_weight_scalar: float = 1.2

    def _explicit_visual_tuning_bound(self, instance_latents: np.ndarray, prompt_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculates the reinforced alignment between localized visual instances 
        and explicit semantic prompt instructions.
        instance_latents: (Batch, Num_Instances, Hidden_Dim)
        prompt_embeddings: (Batch, Hidden_Dim)
        """
        # (Batch, Num_Instances, Hidden) * (Batch, 1, Hidden) -> Sum along Hidden
        prompts_expanded = np.expand_dims(prompt_embeddings, axis=1)
        inst_alignment = np.sum(instance_latents * prompts_expanded, axis=-1)
        
        # Apply scaling based on visual prompt instruction tuning theory
        boosted_alignment = inst_alignment * self.prompt_weight_scalar
        
        return boosted_alignment

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "instance_feature_map" not in payload or "instruction_prompt_latent" not in payload:
                return err("Missing visual instance features or instruction latents for Inst-IT analysis.")
                
            instances = np.array(payload["instance_feature_map"], dtype=np.float32)
            prompt = np.array(payload["instruction_prompt_latent"], dtype=np.float32)

            if instances.ndim != 3 or prompt.ndim != 2:
                return err("Instances must be 3D (B, N, D) and Prompt 2D (B, D).")

            alignment_scores = self._explicit_visual_tuning_bound(instances, prompt)
            
            # Diagnostic: Top instance focus
            top_instance_idx = np.argmax(alignment_scores, axis=-1)

            return ok({
                "engine_id": self.engine_id,
                "instance_alignment_matrix": alignment_scores.tolist(),
                "primary_instance_targets": top_instance_idx.tolist(),
                "status": "Inst-IT Visual Prompt Instructions Bounded"
            })
            
        except Exception as e:
            return err(f"Inst-IT prompt tuning failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniInstItPromptEngine",
            "status": "Operational",
            "prompt_boost": self.prompt_weight_scalar
        }
