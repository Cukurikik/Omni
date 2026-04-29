import ctypes

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class EmbeddingLayer:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/nlp_pipelines/tokenizer_ffi.so')
        self.lib.omni_tokenize_and_embed.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_tokenize_and_embed.restype = ctypes.c_double

    def process_text(self, text: str) -> OmniResult:
        if not text:
            return OmniResult(error="Text cannot be empty")

        err_code = ctypes.c_int(0)
        text_bytes = text.encode('utf-8')
        
        # Simulate embedding vector magnitude
        magnitude = self.lib.omni_tokenize_and_embed(text_bytes, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Tokenization failed with code {err_code.value}")

        return OmniResult(value={'text': text, 'vector_magnitude': magnitude})
