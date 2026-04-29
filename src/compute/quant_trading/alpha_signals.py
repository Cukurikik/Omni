import ctypes

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class AlphaSignals:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/quant_trading/order_matcher_ffi.so')
        self.lib.omni_calculate_vwap.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_calculate_vwap.restype = ctypes.c_double

    def compute_momentum_signal(self, prices: list[float], volumes: list[float]) -> OmniResult:
        if not prices or not volumes or len(prices) != len(volumes):
            return OmniResult(error="Prices and volumes must be equal length and non-empty")

        err_code = ctypes.c_int(0)
        p_arr = (ctypes.c_double * len(prices))(*prices)
        v_arr = (ctypes.c_double * len(volumes))(*volumes)
        
        vwap = self.lib.omni_calculate_vwap(p_arr, v_arr, len(prices), ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"VWAP calculation failed with code {err_code.value}")

        current_price = prices[-1]
        
        # Simple momentum: 1 if above VWAP, -1 if below
        signal = 1 if current_price > vwap else -1
        
        return OmniResult(value={
            'vwap': vwap,
            'signal': signal,
            'strength': abs(current_price - vwap) / vwap
        })
