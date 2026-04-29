import ctypes

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class AdamOptimizer:
    def __init__(self, learning_rate=0.001, beta1=0.9, beta2=0.999):
        self.lr = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.m = None
        self.v = None
        self.t = 0
        
        self.lib = ctypes.CDLL('./system/gradient_optax/gradient_clip_ffi.so')
        self.lib.omni_clip_gradients.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_clip_gradients.restype = None

    def apply_gradients(self, params: list[float], grads: list[float], max_norm: float = 1.0) -> OmniResult:
        if len(params) != len(grads):
            return OmniResult(error="Params and grads must have the same length")

        err_code = ctypes.c_int(0)
        grad_arr = (ctypes.c_double * len(grads))(*grads)
        
        # System layer call: gradient clipping
        self.lib.omni_clip_gradients(grad_arr, len(grads), max_norm, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Gradient clipping failed with code {err_code.value}")

        if self.m is None:
            self.m = [0.0] * len(params)
            self.v = [0.0] * len(params)

        self.t += 1
        new_params = []

        # Deterministic Adam calculation
        for i in range(len(params)):
            g = grad_arr[i]
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * g
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (g * g)
            
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            
            new_param = params[i] - self.lr * m_hat / (v_hat ** 0.5 + 1e-8)
            new_params.append(new_param)

        return OmniResult(value=new_params)
