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
class OmniOmniedgeCompressionEngine:
    """
    OmniOmniedgeCompressionEngine
    Domain: OmniEdge (Tiny ML / Model Compression on Edge Devices)
    Implements hardcore deterministic mathematical weight quantization:
    Translates FP32 weight tensors to symmetric INT8 scale-bounds
    preserving gradient logic implicitly via absolute min-max ranges.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bit_width: int = 8

    def _symmetric_quantize(self, weights: np.ndarray) -> np.ndarray:
        """
        Quantizes weights to INT8 range [-127, 127] preserving 0 at 0.
        Returns the quantized weights and the float scale factor.
        """
        max_val = np.max(np.abs(weights))
        if max_val == 0.0:
            return np.zeros_like(weights, dtype=np.int8), 1.0
            
        q_max = (2 ** (self.bit_width - 1)) - 1
        scale = max_val / q_max
        
        quantized = np.round(weights / scale)
        quantized = np.clip(quantized, -q_max, q_max).astype(np.int8)
        
        return quantized, float(scale)

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "fp32_weights" not in payload:
                return err("Missing 'fp32_weights' argument for edge compression.")
                
            weights = np.array(payload["fp32_weights"], dtype=np.float32)

            q_weights, scale_factor = self._symmetric_quantize(weights)
            
            compression_ratio = float(weights.nbytes) / float(q_weights.nbytes) if q_weights.nbytes > 0 else 1.0

            return ok({
                "engine_id": self.engine_id,
                "quantized_int8_weights": q_weights.tolist(),
                "scale_factor": scale_factor,
                "compression_ratio": compression_ratio,
                "status": "OmniEdge Weights Quantized"
            })
            
        except Exception as e:
            return err(f"OmniEdge compression failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniOmniedgeCompressionEngine",
            "status": "Operational",
            "bit_width": self.bit_width
        }
