import ctypes
from typing import Dict, Any

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class DAGExecutor:
    def __init__(self):
        self.vector_lib = ctypes.CDLL('./system/dataflow_etl/vector_etl_ffi.so')
        self.vector_lib.omni_execute_vector_transform.argtypes = [ctypes.c_size_t, ctypes.POINTER(ctypes.c_int)]
        self.vector_lib.omni_execute_vector_transform.restype = ctypes.c_double

    def execute_dag(self, elements_count: int) -> OmniResult:
        if elements_count <= 0:
            return OmniResult(error="Invalid elements count")

        err_code = ctypes.c_int(0)
        throughput = self.vector_lib.omni_execute_vector_transform(elements_count, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Vector transform failed with code {err_code.value}")

        return OmniResult(value={'throughput_mb_s': throughput})

def run_hamilton_pipeline(data_size: int) -> OmniResult:
    executor = DAGExecutor()
    return executor.execute_dag(data_size)
