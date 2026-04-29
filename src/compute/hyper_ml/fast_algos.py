import ctypes
from typing import List

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class FastMLAlgos:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/hyper_ml/simd_ops_ffi.so')
        self.lib.omni_simd_dot_product.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_simd_dot_product.restype = ctypes.c_double

    def compute_dot_product(self, vec1: List[float], vec2: List[float]) -> OmniResult:
        if len(vec1) != len(vec2) or len(vec1) == 0:
            return OmniResult(error="Vectors must be of equal, non-zero length")

        size = len(vec1)
        ArrType = ctypes.c_double * size
        c_vec1 = ArrType(*vec1)
        c_vec2 = ArrType(*vec2)
        err_code = ctypes.c_int(0)

        result = self.lib.omni_simd_dot_product(c_vec1, c_vec2, size, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"SIMD compute failed with code {err_code.value}")

        return OmniResult(value={'dot_product': result})

def run_fast_dot_product(v1: List[float], v2: List[float]) -> OmniResult:
    algo = FastMLAlgos()
    return algo.compute_dot_product(v1, v2)
