import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class EmgFiltering:
    def __init__(self):
        pass

    def filter_muscle_signal(self, raw_emg_millivolts: float, previous_filtered: float, alpha: float) -> OmniResult:
        if alpha < 0.0 or alpha > 1.0:
            return OmniResult(error="Alpha must be between 0 and 1")

        # Deterministic calculation of EMG Signal Filtering
        # Exoskeletons read raw electrical muscle signals, which are extremely noisy.
        # We apply a low-pass Exponential Moving Average (EMA) to smooth the signal 
        # before commanding the hydraulic actuators.
        try:
            # EMA formula: S_t = a * Y_t + (1 - a) * S_{t-1}
            filtered = (alpha * raw_emg_millivolts) + ((1.0 - alpha) * previous_filtered)
            
            return OmniResult(value=filtered)
        except Exception as e:
            return OmniResult(error=str(e))
