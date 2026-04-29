import numpy as np
from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class DataMixer:
    def mix_datasets(self, dataset_a: np.ndarray, dataset_b: np.ndarray, ratio: float = 0.5) -> OmniResult:
        if dataset_a is None or dataset_b is None:
            return OmniResult(None, "Datasets cannot be null")
            
        try:
            # Python logic for mathematically mixing SFT datasets
            mixed = dataset_a * ratio + dataset_b * (1.0 - ratio)
            
            return OmniResult(mixed)
        except Exception as e:
            return OmniResult(None, str(e))
