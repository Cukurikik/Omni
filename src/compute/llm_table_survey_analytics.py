import numpy as np
from typing import List, Dict, Optional
import omni.compute.monads as monads

@monads.production_compute
def analyze_llm_table_survey(data: np.ndarray) -> monads.Result[Dict[str, float], Exception]:
    if data is None or data.size == 0:
        return monads.Err(ValueError("Dataset cannot be empty"))
    try:
        results = {
            "mean": float(np.mean(data)),
            "std": float(np.std(data)),
            "max": float(np.max(data))
        }
        return monads.Ok(results)
    except Exception as e:
        return monads.Err(e)
