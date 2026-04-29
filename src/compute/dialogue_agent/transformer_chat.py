import ctypes

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class TransformerChat:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/dialogue_agent/kv_cache_ffi.so')
        self.lib.omni_allocate_kv_cache.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_allocate_kv_cache.restype = ctypes.c_double

    def initialize_session(self, sequence_length: int) -> OmniResult:
        if sequence_length <= 0:
            return OmniResult(error="Sequence length must be > 0")

        err_code = ctypes.c_int(0)
        cache_mb = self.lib.omni_allocate_kv_cache(sequence_length, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"KV cache allocation failed: {err_code.value}")

        return OmniResult(value={'cache_allocated_mb': cache_mb})

def start_dialogue_session(seq_len: int) -> OmniResult:
    chat = TransformerChat()
    return chat.initialize_session(seq_len)
