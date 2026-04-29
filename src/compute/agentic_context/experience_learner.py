import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ExperienceLearner:
    def __init__(self, context_dim: int = 256):
        self.dim = context_dim
        self.lib = ctypes.CDLL('./system/agentic_context/memory_index_ffi.so')
        self.lib.omni_update_memory_index.argtypes = [
            ctypes.POINTER(ctypes.c_double), 
            ctypes.POINTER(ctypes.c_double), 
            ctypes.c_int,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_int)
        ]
        self.lib.omni_update_memory_index.restype = None

    def integrate_experience(self, current_state: list[float], new_experience: list[float], learning_rate: float) -> OmniResult:
        if len(current_state) != self.dim or len(new_experience) != self.dim:
            return OmniResult(error="Dimension mismatch for agentic context integration")

        state_arr = (ctypes.c_double * self.dim)(*current_state)
        exp_arr = (ctypes.c_double * self.dim)(*new_experience)
        out_state = (ctypes.c_double * self.dim)()
        err_code = ctypes.c_int(0)

        # FFI call to Rust system layer for memory indexing and state update
        self.lib.omni_update_memory_index(state_arr, exp_arr, self.dim, learning_rate, out_state, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Memory index update failed with code {err_code.value}")

        return OmniResult(value=list(out_state))
