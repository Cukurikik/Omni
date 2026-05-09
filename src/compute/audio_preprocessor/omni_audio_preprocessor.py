"""
omni_audio_preprocessor.py — Audio Preprocessing Pipeline
Inspired by: SoundStorm + Conformer audio preprocessing
Layer: Compute / AI

Production audio preprocessing with mel-spectrogram computation,
voice activity detection, and spectral normalization.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    n_fft: int = 1024
    hop_length: int = 256
    n_mels: int = 80
    fmin: float = 0.0
    fmax: float = 8000.0
    win_length: int = 1024
    power: float = 2.0
    normalized: bool = True
    center: bool = True
    pad_mode: str = "reflect"
    top_db: float = 80.0


class MelFilterBank(nn.Module):
    """Mel-scale filter bank for spectrogram computation."""

    def __init__(self, config: AudioConfig):
        super().__init__()
        self.config = config

        # Build mel filter bank
        fb = self._build_mel_filters(
            config.n_fft, config.n_mels,
            config.sample_rate, config.fmin, config.fmax
        )
        self.register_buffer("mel_fb", fb)

    @staticmethod
    def _hz_to_mel(freq: float) -> float:
        return 2595.0 * math.log10(1.0 + freq / 700.0)

    @staticmethod
    def _mel_to_hz(mel: float) -> float:
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

    def _build_mel_filters(self, n_fft: int, n_mels: int,
                           sample_rate: int, fmin: float,
                           fmax: float) -> torch.Tensor:
        n_freqs = n_fft // 2 + 1

        mel_min = self._hz_to_mel(fmin)
        mel_max = self._hz_to_mel(fmax)

        mel_points = torch.linspace(mel_min, mel_max, n_mels + 2)
        hz_points = torch.tensor([self._mel_to_hz(m.item()) for m in mel_points])
        bin_points = torch.floor((n_fft + 1) * hz_points / sample_rate).long()

        fb = torch.zeros(n_mels, n_freqs)
        for m in range(n_mels):
            f_left = bin_points[m]
            f_center = bin_points[m + 1]
            f_right = bin_points[m + 2]

            for k in range(f_left, f_center):
                if f_center > f_left:
                    fb[m, k] = (k - f_left) / (f_center - f_left)
            for k in range(f_center, f_right):
                if f_right > f_center:
                    fb[m, k] = (f_right - k) / (f_right - f_center)

        return fb

    def forward(self, spectrogram: torch.Tensor) -> torch.Tensor:
        return torch.matmul(self.mel_fb.to(spectrogram.device), spectrogram)


class SpectrogramComputer(nn.Module):
    """Compute magnitude spectrogram from raw audio waveform."""

    def __init__(self, config: AudioConfig):
        super().__init__()
        self.config = config

        # Hann window
        window = torch.hann_window(config.win_length)
        self.register_buffer("window", window)

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        """Compute spectrogram from waveform.

        Args:
            waveform: (batch, samples) raw audio

        Returns:
            spectrogram: (batch, n_freqs, time_frames) magnitude spectrogram
        """
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)

        stft = torch.stft(
            waveform,
            n_fft=self.config.n_fft,
            hop_length=self.config.hop_length,
            win_length=self.config.win_length,
            window=self.window.to(waveform.device),
            center=self.config.center,
            pad_mode=self.config.pad_mode,
            return_complex=True,
        )

        magnitude = stft.abs()
        if self.config.power != 1.0:
            magnitude = magnitude.pow(self.config.power)

        return magnitude


class VoiceActivityDetector(nn.Module):
    """Energy-based voice activity detection."""

    def __init__(self, energy_threshold: float = -40.0,
                 min_speech_duration_ms: int = 250,
                 min_silence_duration_ms: int = 100,
                 sample_rate: int = 16000, hop_length: int = 256):
        super().__init__()
        self.energy_threshold = energy_threshold
        self.min_speech_frames = max(1, int(min_speech_duration_ms * sample_rate
                                             / (hop_length * 1000)))
        self.min_silence_frames = max(1, int(min_silence_duration_ms * sample_rate
                                              / (hop_length * 1000)))

    def forward(self, mel_spec: torch.Tensor) -> torch.Tensor:
        """Detect voice activity from mel spectrogram.

        Args:
            mel_spec: (batch, n_mels, time) mel spectrogram in dB

        Returns:
            vad_mask: (batch, time) boolean mask of speech frames
        """
        energy = mel_spec.mean(dim=1)  # (batch, time)
        is_speech = energy > self.energy_threshold

        # Smooth short gaps
        for b in range(is_speech.shape[0]):
            is_speech[b] = self._smooth_mask(is_speech[b])

        return is_speech

    def _smooth_mask(self, mask: torch.Tensor) -> torch.Tensor:
        """Fill short silence gaps within speech regions."""
        result = mask.clone()
        in_speech = False
        silence_count = 0

        for i in range(len(result)):
            if result[i]:
                if in_speech and silence_count > 0 and silence_count < self.min_silence_frames:
                    # Fill short gap
                    result[max(0, i - silence_count):i] = True
                in_speech = True
                silence_count = 0
            else:
                if in_speech:
                    silence_count += 1
                    if silence_count >= self.min_silence_frames:
                        in_speech = False

        return result


class OmniAudioPreprocessor(nn.Module):
    """Complete audio preprocessing pipeline.

    Takes raw waveforms and produces normalized mel spectrograms
    with optional voice activity detection and length normalization.
    """

    def __init__(self, config: AudioConfig = AudioConfig()):
        super().__init__()
        self.config = config
        self.spectrogram = SpectrogramComputer(config)
        self.mel_bank = MelFilterBank(config)
        self.vad = VoiceActivityDetector(
            sample_rate=config.sample_rate,
            hop_length=config.hop_length,
        )

    def forward(self, waveform: torch.Tensor,
                apply_vad: bool = False) -> Dict[str, torch.Tensor]:
        """Process raw audio waveform.

        Args:
            waveform: (batch, samples) raw audio at config.sample_rate
            apply_vad: whether to apply voice activity detection

        Returns:
            dict with 'mel_spec', 'log_mel', 'vad_mask', 'lengths'
        """
        # Compute spectrogram
        spec = self.spectrogram(waveform)

        # Apply mel filter bank
        mel = self.mel_bank(spec)

        # Log mel
        log_mel = torch.clamp(mel, min=1e-10).log10()

        # Dynamic range compression
        if self.config.top_db > 0:
            max_val = log_mel.amax(dim=(-2, -1), keepdim=True)
            log_mel = torch.maximum(log_mel, max_val - self.config.top_db / 10.0)

        # Normalize
        if self.config.normalized:
            mean = log_mel.mean(dim=-1, keepdim=True)
            std = log_mel.std(dim=-1, keepdim=True).clamp(min=1e-5)
            log_mel = (log_mel - mean) / std

        result = {
            "mel_spec": mel,
            "log_mel": log_mel,
            "lengths": torch.tensor([log_mel.shape[-1]] * log_mel.shape[0]),
        }

        if apply_vad:
            vad_mask = self.vad(log_mel)
            result["vad_mask"] = vad_mask

        return result

    def compute_output_length(self, input_samples: int) -> int:
        """Compute output frame count for given input sample count."""
        if self.config.center:
            return input_samples // self.config.hop_length + 1
        return (input_samples - self.config.n_fft) // self.config.hop_length + 1
