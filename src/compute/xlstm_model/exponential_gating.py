import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ExponentialGating:
    def __init__(self, hidden_size: int):
        self.hidden_size = hidden_size
        self.lib = ctypes.CDLL('./system/xlstm_model/matrix_memory_ffi.so')
        self.lib.omni_xlstm_gate_update.argtypes = [
            ctypes.POINTER(ctypes.c_double), 
            ctypes.POINTER(ctypes.c_double), 
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_int)
        ]
        self.lib.omni_xlstm_gate_update.restype = None

    def apply_exponential_gating(self, memory_state: list[float], input_gate: list[float]) -> OmniResult:
        if len(memory_state) != self.hidden_size or len(input_gate) != self.hidden_size:
            return OmniResult(error="Dimension mismatch for xLSTM gating")

        mem_arr = (ctypes.c_double * self.hidden_size)(*memory_state)
        in_gate_arr = (ctypes.c_double * self.hidden_size)(*input_gate)
        out_state = (ctypes.c_double * self.hidden_size)()
        err_code = ctypes.c_int(0)

        # System FFI call for exponential memory update (xLSTM specific math)
        self.lib.omni_xlstm_gate_update(mem_arr, in_gate_arr, self.hidden_size, out_state, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"xLSTM gating failed with code {err_code.value}")

        return OmniResult(value=list(out_state))
