import ctypes

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class SequenceModel:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/text_generation/beam_search_ffi.so')
        self.lib.omni_beam_search_decode.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_beam_search_decode.restype = ctypes.c_double

    def generate_sequence(self, vocab_size: int, beam_width: int) -> OmniResult:
        if vocab_size <= 0 or beam_width <= 0:
            return OmniResult(error="Vocabulary and beam width must be > 0")

        err_code = ctypes.c_int(0)
        perplexity = self.lib.omni_beam_search_decode(vocab_size, beam_width, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Beam search decoding failed with code {err_code.value}")

        return OmniResult(value={'perplexity': perplexity, 'beam_width': beam_width})

def run_text_generation(vocab: int, beams: int) -> OmniResult:
    model = SequenceModel()
    return model.generate_sequence(vocab, beams)
