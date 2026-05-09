"""
omni_mel_spectrogram.py — Mel Spectrogram Extraction
Layer: Compute / AI

Implements audio waveform processing to generate log-mel spectrograms.
Features exact STFT, Mel filterbank application, and dynamic range compression.
Zero-mock implementation.
"""

import torch
import torch.nn as nn
import math

class OmniMelSpectrogram(nn.Module):
    def __init__(self, sample_rate: int = 16000, n_fft: int = 400, hop_length: int = 160, n_mels: int = 80):
        super().__init__()
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        
        # Precompute window
        window = torch.hann_window(n_fft)
        self.register_buffer("window", window, persistent=False)
        
        # Precompute Mel Filterbank
        mel_filters = self._create_mel_filterbank(sample_rate, n_fft, n_mels)
        self.register_buffer("mel_filters", mel_filters, persistent=False)

    def _hz_to_mel(self, hz: float) -> float:
        return 2595.0 * math.log10(1.0 + hz / 700.0)

    def _mel_to_hz(self, mel: float) -> float:
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

    def _create_mel_filterbank(self, sr: int, n_fft: int, n_mels: int) -> torch.Tensor:
        f_min = 0.0
        f_max = sr / 2.0
        
        mel_min = self._hz_to_mel(f_min)
        mel_max = self._hz_to_mel(f_max)
        
        mel_points = torch.linspace(mel_min, mel_max, n_mels + 2)
        hz_points = self._mel_to_hz(mel_points)
        
        bin_points = torch.floor((n_fft + 1) * hz_points / sr).long()
        
        fbank = torch.zeros(n_mels, n_fft // 2 + 1)
        
        for i in range(1, n_mels + 1):
            left = bin_points[i - 1]
            center = bin_points[i]
            right = bin_points[i + 1]
            
            for j in range(left, center):
                fbank[i - 1, j] = (j - left) / float(center - left)
            for j in range(center, right):
                fbank[i - 1, j] = (right - j) / float(right - center)
                
        return fbank

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        """
        waveform: (Batch, SeqLen)
        """
        # STFT
        stft = torch.stft(
            waveform,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.n_fft,
            window=self.window,
            center=True,
            pad_mode="reflect",
            normalized=False,
            return_complex=True
        )
        
        # Power spectrogram
        power_spec = torch.abs(stft) ** 2
        
        # Mel projection (Batch, NMels, Frames)
        mel_spec = torch.matmul(self.mel_filters, power_spec)
        
        # Log compression (clamp to avoid log(0))
        log_mel = torch.log(torch.clamp(mel_spec, min=1e-5))
        
        return log_mel
