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
class OmniMultiNerdEngine:
    """
    OmniMultiNerdEngine
    Domain: Multilingual NER & Disambiguation
    Mathematically constructs distinct probability boundaries differentiating overlapping 
    entities in multi-genre localized knowledge base contexts.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    disambiguation_margin: float = 0.15

    def _entity_knowledge_affinity(self, token_latents: np.ndarray, knowledge_basis: np.ndarray) -> np.ndarray:
        """
        Calculates cosine similarity bounds differentiating between highly coupled
        linguistic structural representations.
        token_latents: (Batch, Num_Tokens, Hidden)
        knowledge_basis: (Num_Entities, Hidden)
        """
        # Normalize representations
        tokens_norm = token_latents / (np.linalg.norm(token_latents, axis=-1, keepdims=True) + 1e-9)
        kb_norm = knowledge_basis / (np.linalg.norm(knowledge_basis, axis=-1, keepdims=True) + 1e-9)
        
        # Affinity projection via Batched matrix multiplication
        # (Batch, Num_Tokens, Hidden) @ (Hidden, Num_Entities) -> (Batch, Num_Tokens, Num_Entities)
        affinity_matrix = np.matmul(tokens_norm, kb_norm.T)
        
        return affinity_matrix

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "sequence_token_latents" not in payload or "entity_kb_latents" not in payload:
                return err("Missing linguistic or knowledge boundaries for Disambiguation.")
                
            tokens = np.array(payload["sequence_token_latents"], dtype=np.float32)
            kb = np.array(payload["entity_kb_latents"], dtype=np.float32)

            if tokens.ndim != 3 or kb.ndim != 2:
                return err("Latents must be rigorously shaped (Batch, Tokens, D) and (Entities, D).")

            affinity = self._entity_knowledge_affinity(tokens, kb)
            
            # Disambiguation logic: The difference between Top 1 and Top 2 matches
            sorted_affinity = np.sort(affinity, axis=-1)
            top_1 = sorted_affinity[:, :, -1]
            top_2 = sorted_affinity[:, :, -2] if kb.shape[0] >= 2 else np.zeros_like(top_1)
            
            disambiguation_confidence = (top_1 - top_2) > self.disambiguation_margin

            return ok({
                "engine_id": self.engine_id,
                "affinity_scores_shape": list(affinity.shape),
                "firmly_disambiguated_tokens_count": int(np.sum(disambiguation_confidence)),
                "status": "Multi-Genre Entity Disambiguation Bounded"
            })
            
        except Exception as e:
            return err(f"MultiNERD disambiguation logic failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniMultiNerdEngine",
            "status": "Operational",
            "decision_margin": self.disambiguation_margin
        }
