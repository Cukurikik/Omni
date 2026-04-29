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
class OmniMedTokEngine:
    """
    OmniMedTokEngine
    Domain: Multimodal Medical Tokenization
    Mathematically constructs discrete code boundaries for heterogeneous medical data
    (EHR, imaging latents, clinical notes) using Vector Quantization (VQ) codebooks.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    codebook_size: int = 1024

    def _quantize_medical_latent(self, continuous_latents: np.ndarray, codebook: np.ndarray) -> np.ndarray:
        """
        Maps continuous medical vectors to the nearest discrete index in the codebook.
        continuous_latents: (Batch, Hidden_Dim)
        codebook: (Codebook_Size, Hidden_Dim)
        """
        # Calculate L2 distance between tokens and codebook entries
        # (Batch, 1, Hidden) - (1, Codebook, Hidden) -> (Batch, Codebook, Hidden)
        diff = np.expand_dims(continuous_latents, axis=1) - np.expand_dims(codebook, axis=0)
        dist = np.sum(diff**2, axis=-1)
        
        # Get indices of nearest neighbors
        discrete_indices = np.argmin(dist, axis=1)
        
        return discrete_indices

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "medical_latents" not in payload or "tokenizer_codebook" not in payload:
                return err("Missing medical latents or VQ codebook for MedTok discretization.")
                
            latents = np.array(payload["medical_latents"], dtype=np.float32)
            codebook = np.array(payload["tokenizer_codebook"], dtype=np.float32)

            if latents.ndim != 2 or codebook.ndim != 2:
                return err("Medical latents and codebook must be 2D tensors (N, D).")
            if latents.shape[-1] != codebook.shape[-1]:
                return err(f"Dimension mismatch: {latents.shape[-1]} vs {codebook.shape[-1]}")

            tokens = self._quantize_medical_latent(latents, codebook)
            
            # Diagnostic: Codebook usage entropy
            unique_tokens, counts = np.unique(tokens, return_counts=True)
            probs = counts / len(tokens)
            entropy = -np.sum(probs * np.log2(probs + 1e-9))

            return ok({
                "engine_id": self.engine_id,
                "discrete_medical_tokens": tokens.tolist(),
                "codebook_usage_entropy": float(entropy),
                "unique_tokens_in_batch": len(unique_tokens),
                "status": "Medical Data Discretized via VQ-Codebook"
            })
            
        except Exception as e:
            return err(f"MedTok tokenization failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniMedTokEngine",
            "status": "Operational",
            "codebook_capacity": self.codebook_size
        }
