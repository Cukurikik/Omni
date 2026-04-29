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
class OmniMultimodalRecommenderEngine:
    """
    OmniMultimodalRecommenderEngine
    Domain: Awesome-Multimodal-Recommender-Systems
    Implements mathematical collaborative filtering augmented by multimodal feature alignment 
    (visual + textual representation). Computes Matrix Factorization with an added modality bias.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    latent_dim: int = 32

    def _multimodal_mf_predict(self, user_matrix: np.ndarray, item_matrix: np.ndarray, visual_matrix: np.ndarray, text_matrix: np.ndarray, user_vis_pref: np.ndarray, user_txt_pref: np.ndarray) -> np.ndarray:
        """
        Calculates predicted user-item rating matrix:
        R_hat = U * I^T + (U_vis * V^T) + (U_txt * T^T)
        """
        # Collaborative filtering term
        cf_term = np.matmul(user_matrix, item_matrix.T)
        
        # Modality alignment terms
        vis_term = np.matmul(user_vis_pref, visual_matrix.T)
        txt_term = np.matmul(user_txt_pref, text_matrix.T)
        
        # Fusion
        prediction = cf_term + vis_term + txt_term
        return prediction

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "user_embeddings" not in payload or "item_embeddings" not in payload:
                return err("Missing CF user or item representations.")
            if "visual_features" not in payload or "text_features" not in payload:
                return err("Missing multimodal item features (visual/text).")
                
            u = np.array(payload["user_embeddings"], dtype=np.float32)
            i = np.array(payload["item_embeddings"], dtype=np.float32)
            
            v = np.array(payload["visual_features"], dtype=np.float32)
            t = np.array(payload["text_features"], dtype=np.float32)
            
            u_v = np.array(payload.get("user_vis_pref", np.zeros_like(u)), dtype=np.float32)
            u_t = np.array(payload.get("user_txt_pref", np.zeros_like(u)), dtype=np.float32)
            
            # Dimensions check
            if u.shape[1] != i.shape[1] or v.shape[1] != u_v.shape[1] or t.shape[1] != u_t.shape[1]:
                return err("Latent dimension mismatch across modalities.")
            
            if i.shape[0] != v.shape[0] or i.shape[0] != t.shape[0]:
                return err("Item embeddings length must match modality features length.")
                
            y_hat = self._multimodal_mf_predict(u, i, v, t, u_v, u_t)
            
            # Sigmoid scale for scores 0-1
            y_hat_scaled = 1.0 / (1.0 + np.exp(-y_hat))

            return ok({
                "engine_id": self.engine_id,
                "recommender_scores": y_hat_scaled.tolist(),
                "status": "Multimodal Recommendation Computed"
            })
            
        except Exception as e:
            return err(f"Multimodal Recommendation failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniMultimodalRecommenderEngine",
            "status": "Operational",
            "latent_dim_config": self.latent_dim
        }
