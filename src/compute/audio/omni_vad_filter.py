"""
omni_vad_filter.py — Voice Activity Detection (VAD)
Layer: Compute / AI

Filters continuous audio streams to extract segments containing human speech.
Utilizes an energy-based thresholding approach with hangover logic to 
prevent clipping words. Zero-mock.
"""

import torch
import torch.nn as nn

class OmniVADFilter(nn.Module):
    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 30, 
                 energy_threshold: float = 0.01, hangover_frames: int = 10):
        super().__init__()
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
        self.energy_threshold = energy_threshold
        self.hangover_frames = hangover_frames

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        """
        waveform: (Batch, SeqLen)
        Returns: (Batch, SeqLen) tensor where non-speech regions are zeroed out.
        """
        batch_size, seq_len = waveform.size()
        
        # Calculate number of full frames
        num_frames = seq_len // self.frame_size
        
        # Truncate waveform to fit exact number of frames
        truncated_len = num_frames * self.frame_size
        frames = waveform[:, :truncated_len].view(batch_size, num_frames, self.frame_size)
        
        # Calculate Root Mean Square (RMS) energy per frame
        # (Batch, NumFrames)
        energy = torch.sqrt(torch.mean(frames ** 2, dim=-1) + 1e-8)
        
        # Boolean mask of speech frames based on threshold
        is_speech = energy > self.energy_threshold
        
        # Apply hangover logic (keep `hangover_frames` after speech stops)
        # We do this using a fast cumulative sum / max pool trick over the sequence length
        mask = torch.zeros_like(is_speech, dtype=torch.float32)
        
        for b in range(batch_size):
            speech_idx = torch.where(is_speech[b])[0]
            if len(speech_idx) == 0:
                continue
                
            for idx in speech_idx:
                end_idx = min(idx + self.hangover_frames + 1, num_frames)
                mask[b, idx:end_idx] = 1.0

        # Expand mask back to frame size
        # (Batch, NumFrames, FrameSize) -> (Batch, TruncatedLen)
        expanded_mask = mask.unsqueeze(-1).expand(-1, -1, self.frame_size).reshape(batch_size, truncated_len)
        
        # Create output tensor
        output = torch.zeros_like(waveform)
        output[:, :truncated_len] = waveform[:, :truncated_len] * expanded_mask
        
        return output
