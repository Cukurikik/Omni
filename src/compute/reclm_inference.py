import numpy as np
from omni.core import Result, Ok, Err

def run_reclm_inference(features: np.ndarray) -> Result[float, Exception]:
    if features.size == 0:
        return Err(ValueError("Empty features"))
    return Ok(float(np.sum(features) * 0.5))
