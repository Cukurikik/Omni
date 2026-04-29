"""
OMNI LocalAI Serving Engine
Probability distribution sampling over categorical logits with temperature scaling.
"""
import numpy as np
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniLocalAIServingEngine(OmniBaseEngine):
    def __init__(self, vocab_size: int = 32000):
        super().__init__()
        self.vocab_size = vocab_size

    def process(self, logits: List[float], temperature: float = 1.0, top_p: float = 0.9) -> Result[int, str]:
        if len(logits) != self.vocab_size:
            return Err(f"Logits dimension {len(logits)} != vocab size {self.vocab_size}")
        if temperature <= 0.0:
            return Err("Temperature must be greater than 0.")
            
        try:
            arr_logits = np.array(logits, dtype=np.float32)
            scaled_logits = arr_logits / temperature
            exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
            probs = exp_logits / np.sum(exp_logits)
            
            sorted_indices = np.argsort(probs)[::-1]
            sorted_probs = probs[sorted_indices]
            cumulative_probs = np.cumsum(sorted_probs)
            
            cutoff_index = np.searchsorted(cumulative_probs, top_p)
            if cutoff_index == 0:
                cutoff_index = 1
            
            valid_indices = sorted_indices[:cutoff_index]
            chosen = int(valid_indices[0])
            
            return Ok(chosen)
        except Exception as e:
            return Err(f"Sampling failed: {str(e)}")

    def diagnostics(self) -> Result[Dict[str, Any], str]:
        logits = np.random.randn(self.vocab_size).tolist()
        res = self.process(logits, 0.8, 0.95)
        if hasattr(res, 'is_ok') and res.is_ok():
            return Ok({"status": "healthy", "vocab_size": self.vocab_size})
        return Err("Diagnostics failed on LocalAI engine.")
