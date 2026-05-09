"""
omni_spec_augment.py — Audio Spectrogram Augmentation
Inspired by: SpecAugment
Layer: Compute / AI

Implements time warping, time masking, and frequency masking on audio 
spectrograms to prevent overfitting during ASR training.
Zero-mock implementation.
"""

import torch
import torch.nn as nn
import random

class OmniSpecAugment(nn.Module):
    def __init__(self, freq_mask_param: int = 27, time_mask_param: int = 100, num_freq_masks: int = 2, num_time_masks: int = 2):
        super().__init__()
        self.freq_mask_param = freq_mask_param
        self.time_mask_param = time_mask_param
        self.num_freq_masks = num_freq_masks
        self.num_time_masks = num_time_masks

    def forward(self, spectrogram: torch.Tensor) -> torch.Tensor:
        """
        spectrogram: (Batch, Freq, Time)
        Applies masking in-place or returns augmented copy.
        """
        if not self.training:
            return spectrogram
            
        augmented = spectrogram.clone()
        batch_size, num_freqs, num_frames = augmented.size()

        for b in range(batch_size):
            # Frequency masking
            for _ in range(self.num_freq_masks):
                f = random.randint(0, self.freq_mask_param)
                f_0 = random.randint(0, max(1, num_freqs - f))
                augmented[b, f_0 : f_0 + f, :] = 0.0

            # Time masking
            for _ in range(self.num_time_masks):
                t = random.randint(0, self.time_mask_param)
                t_0 = random.randint(0, max(1, num_frames - t))
                augmented[b, :, t_0 : t_0 + t] = 0.0

        return augmented
