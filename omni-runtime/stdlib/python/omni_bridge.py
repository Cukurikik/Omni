# ============================================================
# OMNI Python Bridge — ctypes Zero-Copy Nexus
# ============================================================
# Layer: Compute (ML, Data Science, Scripting)
# Python menggunakan ctypes bawaan — TIDAK perlu pip install.
# ============================================================

import ctypes
import os
import sys
from ctypes import c_void_p, c_size_t, c_char_p, c_uint8, POINTER, Structure

# Path dinamis ke kernel DLL/SO berdasarkan platform
_PLATFORM_EXT = {
    'win32': 'omni_core.dll',
    'linux': 'libomni_core.so',
    'darwin': 'libomni_core.dylib',
}

_LIB_NAME = _PLATFORM_EXT.get(sys.platform, 'libomni_core.so')
_LIB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', 'core', 'target', 'release', _LIB_NAME
)


class OmniBuffer(Structure):
    """Mapping struct ke Rust OmniBuffer (Phase 11)"""
    _fields_ = [
        ("ptr", c_void_p),
        ("len", c_size_t),
        ("capacity", c_size_t),
    ]


class OmniBridge:
    """Jembatan utama Python ↔ OMNI Kernel"""

    def __init__(self):
        if not os.path.exists(_LIB_PATH):
            raise FileNotFoundError(
                f"[OMNI-E104] Kernel tidak ditemukan: {_LIB_PATH}\n"
                "Kompilasi dengan: omni build --release"
            )
        self._lib = ctypes.CDLL(_LIB_PATH)
        self._setup_ffi()

    def _setup_ffi(self):
        """Mendefinisikan signature C-ABI untuk semua fungsi OMNI"""
        # __omni_ffi(args_buffer: *const u8, len: usize) -> *mut u8
        self._lib.__omni_ffi.argtypes = [c_void_p, c_size_t]
        self._lib.__omni_ffi.restype = c_void_p

    def execute(self, function_name: str, data: bytes) -> int:
        """
        Eksekusi fungsi OMNI melalui C-ABI.
        Returns: pointer address (untuk dibaca via numpy atau ctypes)
        """
        buf = ctypes.create_string_buffer(data)
        result_ptr = self._lib.__omni_ffi(buf, len(data))
        return result_ptr

    def execute_zero_copy(self, function_name: str, numpy_array):
        """
        Kirim numpy array langsung ke Rust tanpa copy.
        numpy_array.ctypes.data → pointer mentah → Rust NonNull<u8>
        """
        import numpy as np
        if not isinstance(numpy_array, np.ndarray):
            raise TypeError("[OMNI-E105] Harus numpy.ndarray untuk zero-copy")

        data_ptr = numpy_array.ctypes.data_as(c_void_p)
        data_len = numpy_array.nbytes
        return self._lib.__omni_ffi(data_ptr, data_len)


# Singleton global
bridge = OmniBridge() if os.path.exists(_LIB_PATH) else None
