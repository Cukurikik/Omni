import numpy as np

def omni_matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if a.shape[1] != b.shape[0]:
        raise ValueError("Matrix dimensions must align")
    return np.matmul(a, b)
