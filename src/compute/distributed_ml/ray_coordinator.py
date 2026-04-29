import ctypes
from typing import List

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class RayCoordinator:
    def __init__(self):
        self.kube_lib = ctypes.CDLL('./system/distributed_ml/kube_ffi.so')
        self.kube_lib.omni_schedule_pod.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.kube_lib.omni_schedule_pod.restype = ctypes.c_int

    def schedule_tasks(self, num_tasks: int) -> OmniResult:
        err_code = ctypes.c_int(0)
        scheduled = self.kube_lib.omni_schedule_pod(num_tasks, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Pod scheduling failed with code {err_code.value}")

        return OmniResult(value={'scheduled_pods': scheduled})

def distribute_training_job(num_workers: int) -> OmniResult:
    coordinator = RayCoordinator()
    return coordinator.schedule_tasks(num_workers)
