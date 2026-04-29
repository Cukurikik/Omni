import numpy as np
import math
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniEasyInstructEngine(OmniBaseEngine):
    """
    OMNI MOTHER - BATCH 17 DEEP ARCHITECTURE - SEMESTER 12
    Instruction processing complexity scorer via entropy

    Mathematical Operation: instruction_complexity_scoring
    Zero-Mock: All computations use numpy/math primitives.
    Monadic Interface: Result[T, E] enforced.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.engine_name = "OmniEasyInstructEngine"
        self.config = kwargs

    def process(self, payload: Any) -> Result[Dict[str, Any], Exception]:
        try:
            if not isinstance(payload, dict):
                return Err(ValueError("Payload must be a dictionary."))
            data = payload.get("data", [])
            if not isinstance(data, list) or len(data) == 0:
                return Err(ValueError("Payload must contain non-empty data array."))
            config = self.config

            data = np.array(payload['data'], dtype=np.float64)
            freqs = np.abs(data) + 1e-8
            probs = freqs / np.sum(freqs)
            entropy = -float(np.sum(probs * np.log2(probs + 1e-12)))
            max_entropy = np.log2(len(data)) if len(data) > 1 else 1.0
            complexity_score = entropy / max_entropy
            kernel_output = float(complexity_score)

            return Ok({
                "engine": self.engine_name,
                "operation": "instruction_complexity_scoring",
                "kernel_output": kernel_output,
            })
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Result[Dict[str, Any], Exception]:
        try:
            res = self.process({"data": [1.0, 2.0, -0.5, 3.14]})
            if hasattr(res, "is_ok") and res.is_ok():
                return Ok({"status": "healthy", "engine": self.engine_name})
            return Err(RuntimeError("Diagnostic failed"))
        except Exception as e:
            return Err(e)
