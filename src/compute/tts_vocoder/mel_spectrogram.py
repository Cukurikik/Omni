import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MelSpectrogram:
    def __init__(self, sample_rate=22050, n_fft=1024, n_mels=80):
        self.sr = sample_rate
        self.n_fft = n_fft
        self.n_mels = n_mels
        
        self.lib = ctypes.CDLL('./system/tts_vocoder/griffin_lim_ffi.so')
        self.lib.omni_griffin_lim.argtypes = [
            ctypes.POINTER(ctypes.c_double), 
            ctypes.c_int, 
            ctypes.c_int, 
            ctypes.POINTER(ctypes.c_double), 
            ctypes.POINTER(ctypes.c_int)
        ]
        self.lib.omni_griffin_lim.restype = None

    def invert_to_audio(self, mel_spec: list[float], length: int) -> OmniResult:
        if len(mel_spec) == 0:
            return OmniResult(error="Empty mel spectrogram provided")

        mel_arr = (ctypes.c_double * len(mel_spec))(*mel_spec)
        out_audio = (ctypes.c_double * length)()
        err_code = ctypes.c_int(0)

        # FFI call to C system layer for fast phase reconstruction
        self.lib.omni_griffin_lim(mel_arr, len(mel_spec), length, out_audio, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"Griffin-Lim vocoder failed with code {err_code.value}")

        return OmniResult(value=list(out_audio))
