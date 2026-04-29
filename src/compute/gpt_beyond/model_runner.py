import ctypes
import numpy as np

# Load C++ backend for attention
try:
    _lib = ctypes.CDLL("./omni_gpt_beyond.so")
except:
    _lib = None

def run_fast_attention(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> np.ndarray:
    seq_len, dim = q.shape
    out = np.zeros_like(q)
    if _lib:
        _lib.compute_attention(
            q.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            k.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            v.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            out.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            seq_len, dim
        )
    return out
