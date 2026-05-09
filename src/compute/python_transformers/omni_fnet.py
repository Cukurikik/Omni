"""OMNI Compute — FNet (Fourier Transform Mixing)"""
import logging
import cmath
from typing import List

logger = logging.getLogger("omni.fnet")

class FNetMixer:
    """
    FNet: Mixing Tokens with Fourier Transforms.
    Replaces Self-Attention with a parameter-free 2D Discrete Fourier Transform.
    """
    def __init__(self, seq_len: int, d_model: int):
        self.seq_len = seq_len
        self.d_model = d_model
        logger.info("Initialized FNet Fourier Mixer")

    def _fft_1d(self, x: List[complex]) -> List[complex]:
        """Cooley-Tukey 1D FFT simulation (O(N log N))."""
        N = len(x)
        if N <= 1: return x
        even = self._fft_1d(x[0::2])
        odd = self._fft_1d(x[1::2])
        T = [cmath.exp(-2j * cmath.pi * k / N) * odd[k] for k in range(N // 2)]
        return [even[k] + T[k] for k in range(N // 2)] + [even[k] - T[k] for k in range(N // 2)]

    def forward(self, hidden_states: List[List[float]]) -> List[List[float]]:
        """Applies 2D FFT: first along hidden dimension, then along sequence length."""
        # 1. FFT along hidden dimension (for each token)
        fft_d = []
        for i in range(self.seq_len):
            row_complex = [complex(val, 0) for val in hidden_states[i]]
            # Pad to power of 2 for simplicity if needed, but assuming d_model is power of 2
            fft_d.append(self._fft_1d(row_complex))
            
        # 2. FFT along sequence dimension (for each feature)
        output = [[0.0]*self.d_model for _ in range(self.seq_len)]
        for d in range(self.d_model):
            col_complex = [fft_d[i][d] for i in range(self.seq_len)]
            fft_seq = self._fft_1d(col_complex)
            for i in range(self.seq_len):
                output[i][d] = fft_seq[i].real # Keep only real part for next layers
                
        return output
