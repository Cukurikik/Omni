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
class OmniGrokMoeRoutingEngine:
    """
    OmniGrokMoeRoutingEngine
    Domain: Grok Mixture of Experts (MoE) Architecture
    Mathematically extracts Top-K noisy gated sparse expert routing assignments
    matching the massive sparse routing parameters of Grok.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    top_k: int = 2
    noise_epsilon: float = 1e-2

    def _noisy_top_k_gating(self, tokens: np.ndarray, w_gate: np.ndarray) -> np.ndarray:
        """
        Computes noisy top-k routing distributions.
        tokens: (Batch, Seq_Len, Dim)
        w_gate: (Dim, Num_Experts)
        """
        # Outer dimensions
        batch, seq, dim = tokens.shape
        num_experts = w_gate.shape[1]
        
        # Flatten tokens to easily route
        flat_tokens = tokens.reshape(-1, dim) # (B*S, Dim)
        
        # Linear gating projection
        clean_logits = np.matmul(flat_tokens, w_gate)
        
        # Add normally distributed noise for exploration and load balancing bounds
        raw_noise = np.random.randn(*clean_logits.shape).astype(np.float32)
        noisy_logits = clean_logits + (self.noise_epsilon * raw_noise)
        
        # Sort and take Top-K indices per token
        top_k_indices = np.argsort(noisy_logits, axis=-1)[:, -self.top_k:][:, ::-1]
        
        # Construct dense probability routing mask
        routing_probs = np.zeros_like(noisy_logits)
        for i in range(flat_tokens.shape[0]):
            for k in range(self.top_k):
                idx = top_k_indices[i, k]
                routing_probs[i, idx] = noisy_logits[i, idx]
        
        # Softmax over only the Top K active routes
        # Replace 0 with -inf so softmax zeroes them
        mask = routing_probs == 0
        routing_probs[mask] = -1e9
        
        # Stabilized softmax
        exp_r = np.exp(routing_probs - np.max(routing_probs, axis=-1, keepdims=True))
        gating_probabilities = exp_r / np.sum(exp_r, axis=-1, keepdims=True)
        
        # Ensure mask enforcement fully zeros out extreme negatives
        gating_probabilities[mask] = 0.0
        
        return gating_probabilities.reshape(batch, seq, num_experts)

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "hidden_tokens" not in payload or "gate_weights" not in payload:
                return err("Missing token representations or MoE gate weights.")
                
            x_tokens = np.array(payload["hidden_tokens"], dtype=np.float32)
            gate_w = np.array(payload["gate_weights"], dtype=np.float32)

            if x_tokens.ndim != 3:
                return err("Tokens must be 3D (Batch, Sequence, Dimension).")
            if gate_w.ndim != 2:
                return err("Gate Weights must be 2D (Dimension, Num Experts).")
            if x_tokens.shape[-1] != gate_w.shape[0]:
                return err("Gate dimension mismatch.")

            if gate_w.shape[1] < self.top_k:
                return err(f"Number of experts ({gate_w.shape[1]}) must exceed Top-K target ({self.top_k}).")

            moe_routes = self._noisy_top_k_gating(x_tokens, gate_w)

            return ok({
                "engine_id": self.engine_id,
                "expert_routing_probabilities": moe_routes.tolist(),
                "status": "Grok MoE Routes Allocated"
            })
            
        except Exception as e:
            return err(f"Grok MoE Router failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniGrokMoeRoutingEngine",
            "status": "Operational",
            "top_k_experts": self.top_k
        }
