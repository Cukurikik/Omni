import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class EntityEmbedding:
    def __init__(self, embedding_dim: int):
        self.dim = embedding_dim
        self.lib = ctypes.CDLL('./system/ampligraph_kg/triple_store_ffi.so')
        self.lib.omni_calculate_transe_distance.argtypes = [
            ctypes.POINTER(ctypes.c_double), 
            ctypes.POINTER(ctypes.c_double), 
            ctypes.POINTER(ctypes.c_double), 
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_int)
        ]
        self.lib.omni_calculate_transe_distance.restype = None

    def calculate_distance(self, head: list[float], relation: list[float], tail: list[float]) -> OmniResult:
        if len(head) != self.dim or len(relation) != self.dim or len(tail) != self.dim:
            return OmniResult(error="Dimension mismatch between embeddings and configured dim")

        h_arr = (ctypes.c_double * self.dim)(*head)
        r_arr = (ctypes.c_double * self.dim)(*relation)
        t_arr = (ctypes.c_double * self.dim)(*tail)
        
        distance = ctypes.c_double(0.0)
        err_code = ctypes.c_int(0)
        
        # System layer FFI call
        self.lib.omni_calculate_transe_distance(h_arr, r_arr, t_arr, self.dim, ctypes.byref(distance), ctypes.byref(err_code))
        
        if err_code.value != 0:
            return OmniResult(error=f"TransE distance calculation failed with code {err_code.value}")

        return OmniResult(value=distance.value)
