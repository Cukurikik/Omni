import ctypes

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class TorchMetricsEvaluator:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/ml_metrics/tensor_metrics_ffi.so')
        self.lib.omni_compute_accuracy.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_compute_accuracy.restype = ctypes.c_double

    def evaluate_batch(self, correct: int, total: int) -> OmniResult:
        if total <= 0:
            return OmniResult(error="Total must be greater than zero")

        err_code = ctypes.c_int(0)
        accuracy = self.lib.omni_compute_accuracy(correct, total, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Metric calculation failed with code {err_code.value}")

        return OmniResult(value={'accuracy': accuracy})

def run_evaluation(correct_preds: int, total_preds: int) -> OmniResult:
    evaluator = TorchMetricsEvaluator()
    return evaluator.evaluate_batch(correct_preds, total_preds)
