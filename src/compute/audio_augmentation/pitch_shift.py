import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class AudioAugmenter:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/audio_augmentation/dsp_kernel_ffi.so')
        self.lib.omni_apply_pitch_shift.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_apply_pitch_shift.restype = None

    def pitch_shift(self, audio_data: list[float], semitones: float) -> OmniResult:
        if not audio_data:
            return OmniResult(error="Audio data cannot be empty")

        err_code = ctypes.c_int(0)
        data_arr = (ctypes.c_double * len(audio_data))(*audio_data)
        
        self.lib.omni_apply_pitch_shift(data_arr, len(audio_data), semitones, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"DSP Pitch Shift failed with code {err_code.value}")

        return OmniResult(value=list(data_arr))
