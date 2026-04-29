import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class CrossModalAttention:
    def __init__(self, embed_dim: int):
        self.dim = embed_dim
        self.lib = ctypes.CDLL('./system/multimodal_search/cosine_sim_ffi.so')
        self.lib.omni_cosine_similarity.argtypes = [
            ctypes.POINTER(ctypes.c_double), 
            ctypes.POINTER(ctypes.c_double), 
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_int)
        ]
        self.lib.omni_cosine_similarity.restype = None

    def calculate_attention_score(self, text_embed: list[float], image_embed: list[float]) -> OmniResult:
        if len(text_embed) != self.dim or len(image_embed) != self.dim:
            return OmniResult(error="Embedding dimensions must match the initialized dimension")

        t_arr = (ctypes.c_double * self.dim)(*text_embed)
        i_arr = (ctypes.c_double * self.dim)(*image_embed)
        
        score = ctypes.c_double(0.0)
        err_code = ctypes.c_int(0)
        
        # System FFI call for high-speed dot-product/cosine sim
        self.lib.omni_cosine_similarity(t_arr, i_arr, self.dim, ctypes.byref(score), ctypes.byref(err_code))
        
        if err_code.value != 0:
            return OmniResult(error=f"Cosine similarity calculation failed with code {err_code.value}")

        # Deterministic softmax-like normalization simulation
        attention_weight = math.exp(score.value) / (math.exp(score.value) + math.exp(1.0 - score.value))

        return OmniResult(value=attention_weight)
