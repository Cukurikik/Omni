"""
omni_mfcc_extractor.py — Mel-Frequency Cepstral Coefficients
Layer: Compute / Audio
Inspired by: librosa

Implements raw mathematical extraction of MFCCs from a waveform.
Converts audio into the frequency domain via STFT, applies Mel filterbanks
to map to human-perceptive scales, and compresses via DCT. Zero mock.
"""

import numpy as np

class OmniMFCCExtractor:
    def __init__(self, sample_rate: int = 16000, n_mfcc: int = 20, n_mels: int = 40, n_fft: int = 512, hop_length: int = 160):
        self.sr = sample_rate
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length
        
        # Precompute Mel Filterbank
        self.mel_basis = self._create_mel_filterbank()
        # Precompute DCT Basis
        self.dct_basis = self._create_dct_basis()

    def _hz_to_mel(self, hz: float) -> float:
        return 2595.0 * np.log10(1.0 + hz / 700.0)

    def _mel_to_hz(self, mel: float) -> float:
        return 700.0 * (10.0**(mel / 2595.0) - 1.0)

    def _create_mel_filterbank(self) -> np.ndarray:
        # Mel points from 0Hz to Nyquist (sr/2)
        fmin, fmax = 0.0, self.sr / 2.0
        mel_min, mel_max = self._hz_to_mel(fmin), self._hz_to_mel(fmax)
        
        mel_points = np.linspace(mel_min, mel_max, self.n_mels + 2)
        hz_points = self._mel_to_hz(mel_points)
        
        # Bin indices for FFT
        fft_bins = np.floor((self.n_fft + 1) * hz_points / self.sr).astype(int)
        
        # Construct triangular filters
        weights = np.zeros((self.n_mels, int(1 + self.n_fft // 2)))
        for i in range(1, self.n_mels + 1):
            left, center, right = fft_bins[i-1], fft_bins[i], fft_bins[i+1]
            
            for j in range(left, center):
                weights[i-1, j] = (j - left) / (center - left)
            for j in range(center, right):
                weights[i-1, j] = (right - j) / (right - center)
                
        # Slaney-style normalization
        enorm = 2.0 / (hz_points[2:self.n_mels+2] - hz_points[:self.n_mels])
        weights *= enorm[:, np.newaxis]
        
        return weights

    def _create_dct_basis(self) -> np.ndarray:
        n = np.arange(self.n_mels)
        k = np.arange(self.n_mfcc)[:, np.newaxis]
        basis = np.cos(np.pi * k * (2 * n + 1) / (2 * self.n_mels))
        basis[0] *= 1.0 / np.sqrt(2.0)
        basis *= np.sqrt(2.0 / self.n_mels)
        return basis

    def process(self, waveform: np.ndarray) -> np.ndarray:
        """
        waveform: 1D numpy array of audio samples
        Returns: (n_mfcc, Frames)
        """
        # 1. Framing
        num_frames = 1 + (len(waveform) - self.n_fft) // self.hop_length
        frames = np.zeros((num_frames, self.n_fft))
        for i in range(num_frames):
            frames[i] = waveform[i * self.hop_length : i * self.hop_length + self.n_fft]
            
        # 2. Windowing (Hann)
        window = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(self.n_fft) / (self.n_fft - 1))
        frames *= window
        
        # 3. FFT & Power Spectrum
        fft_mag = np.abs(np.fft.rfft(frames, n=self.n_fft, axis=1))
        power_spec = (fft_mag ** 2) / self.n_fft
        
        # 4. Mel Filterbank
        # (Frames, n_fft/2) @ (n_fft/2, n_mels) -> (Frames, n_mels)
        mel_spec = np.dot(power_spec, self.mel_basis.T)
        
        # 5. Log operation
        log_mel_spec = 10.0 * np.log10(np.maximum(1e-10, mel_spec))
        
        # 6. Discrete Cosine Transform (DCT-II)
        # (n_mfcc, n_mels) @ (n_mels, Frames) -> (n_mfcc, Frames)
        mfcc = np.dot(self.dct_basis, log_mel_spec.T)
        
        return mfcc
