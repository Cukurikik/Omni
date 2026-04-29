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
class OmniOmegaBittensorSubnetEngine:
    """
    OmniOmegaBittensorSubnetEngine
    Domain: omegalabs-bittensor-subnet (Decentralized AGI Multimodal Dataset)
    Computes a deterministic reward mechanism and node weight assignment
    based on miner submission alignment against evaluation consensus logic.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alpha: float = 0.1  # EMA smoothing factor
    
    def _calculate_miner_rewards(self, predictions: np.ndarray, ground_truth: np.ndarray, response_latency: np.ndarray) -> np.ndarray:
        """
        Calculates multimodal miner rewards using similarity alignment and latency penalty.
        predictions: (Miners, Features)
        ground_truth: (Features,)
        response_latency: (Miners,)
        """
        # Normalize vectors for Cosine Similarity
        p_norm = predictions / (np.linalg.norm(predictions, axis=1, keepdims=True) + 1e-12)
        gt_norm = ground_truth / (np.linalg.norm(ground_truth) + 1e-12)
        
        # Alignment Score [0, 1]
        cosine_sim = np.dot(p_norm, gt_norm)
        base_score = np.clip((cosine_sim + 1.0) / 2.0, 0.0, 1.0)
        
        # Latency Penalty (Exponential decay based on latency)
        # Assuming latency is normalized between 0.0 and 1.0 (where 1.0 is max timeout)
        latency_penalty = np.exp(-3.0 * response_latency)
        
        final_reward = base_score * latency_penalty
        return final_reward

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "miner_predictions" not in payload or "ground_truth" not in payload or "historic_weights" not in payload:
                return err("Missing inputs for Subnet Reward calculation.")
                
            predictions = np.array(payload["miner_predictions"], dtype=np.float32)
            ground_truth = np.array(payload["ground_truth"], dtype=np.float32)
            historic_w = np.array(payload["historic_weights"], dtype=np.float32)
            
            # Default latency to 0 if not provided
            latency = np.array(payload.get("response_latency", np.zeros(predictions.shape[0])), dtype=np.float32)

            if predictions.ndim != 2:
                return err("Predictions must be (Miners, Features)")
            if ground_truth.ndim != 1 or ground_truth.shape[0] != predictions.shape[1]:
                return err("Ground truth shape must match feature size.")
            if historic_w.shape[0] != predictions.shape[0]:
                return err("Historic weights count must match Miners count.")
                
            rewards = self._calculate_miner_rewards(predictions, ground_truth, latency)
            
            # Update historic weights using EMA
            updated_weights = (self.alpha * rewards) + ((1.0 - self.alpha) * historic_w)
            
            # Re-normalize weights across the subnet
            updated_weights /= (np.sum(updated_weights) + 1e-12)

            return ok({
                "engine_id": self.engine_id,
                "miner_rewards": rewards.tolist(),
                "updated_subnet_weights": updated_weights.tolist(),
                "status": "Subnet Rewards Distributed"
            })
            
        except Exception as e:
            return err(f"Bittensor subnet evaluation failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniOmegaBittensorSubnetEngine",
            "status": "Operational",
            "ema_smoothing_alpha": self.alpha
        }
