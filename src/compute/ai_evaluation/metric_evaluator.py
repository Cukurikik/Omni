import ctypes

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MetricEvaluator:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/ai_evaluation/drift_detector_ffi.so')
        self.lib.omni_detect_drift.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_detect_drift.restype = ctypes.c_double

    def evaluate_model_metrics(self, accuracy_history: list[float]) -> OmniResult:
        if not accuracy_history:
            return OmniResult(error="Accuracy history cannot be empty")

        err_code = ctypes.c_int(0)
        history_arr = (ctypes.c_double * len(accuracy_history))(*accuracy_history)
        
        # Calculate drift score mathematically
        drift_score = self.lib.omni_detect_drift(history_arr, len(accuracy_history), ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Drift detection failed with code {err_code.value}")

        return OmniResult(value={
            'drift_score': drift_score,
            'status': 'DEGRADED' if drift_score > 0.5 else 'STABLE'
        })
