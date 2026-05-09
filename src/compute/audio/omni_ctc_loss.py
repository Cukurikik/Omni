"""
omni_ctc_loss.py — Connectionist Temporal Classification
Layer: Compute / AI

Provides a zero-mock wrapper for PyTorch's CTCLoss, correctly configuring
sequence length reductions and blank token index targeting for speech recognition.
"""

import torch
import torch.nn as nn

class OmniCTCLoss(nn.Module):
    """
    Computes the Connectionist Temporal Classification loss between continuous 
    unsegmented time series (audio model outputs) and target sequences (transcripts).
    """
    def __init__(self, blank_idx: int = 0, reduction: str = 'mean', zero_infinity: bool = True):
        super().__init__()
        self.blank_idx = blank_idx
        self.reduction = reduction
        self.zero_infinity = zero_infinity
        
        # PyTorch native CTCLoss implementation handles the dynamic programming algorithm
        self.ctc_criterion = nn.CTCLoss(
            blank=self.blank_idx, 
            reduction=self.reduction, 
            zero_infinity=self.zero_infinity
        )

    def forward(self, log_probs: torch.Tensor, targets: torch.Tensor, input_lengths: torch.Tensor, target_lengths: torch.Tensor) -> torch.Tensor:
        """
        log_probs: Tensor of shape (InputSeqLen, BatchSize, NumClasses). 
                   Must contain log-probabilities (e.g., via log_softmax).
        targets: Tensor of shape (BatchSize, MaxTargetLen) or concatenated 1D tensor.
        input_lengths: Tensor of shape (BatchSize,) indicating valid lengths of inputs.
        target_lengths: Tensor of shape (BatchSize,) indicating valid lengths of targets.
        """
        # Ensure log_probs is (T, N, C) for CTCLoss if it was passed as (N, T, C)
        if log_probs.size(1) != input_lengths.size(0) and log_probs.size(0) == input_lengths.size(0):
            log_probs = log_probs.transpose(0, 1)
            
        loss = self.ctc_criterion(log_probs, targets, input_lengths, target_lengths)
        return loss

    def decode_greedy(self, log_probs: torch.Tensor, input_lengths: torch.Tensor) -> list:
        """
        Utility for fast greedy decoding of CTC output (collapse repeated, remove blanks).
        """
        # (T, N, C) -> (N, T, C)
        if log_probs.size(0) != input_lengths.size(0) and log_probs.size(1) == input_lengths.size(0):
             log_probs = log_probs.transpose(0, 1)
             
        predictions = torch.argmax(log_probs, dim=-1)
        decoded_batch = []
        
        for i in range(predictions.size(0)):
            valid_len = input_lengths[i].item()
            pred_seq = predictions[i, :valid_len].tolist()
            
            # Collapse repeated and remove blanks
            collapsed = []
            prev_token = -1
            for token in pred_seq:
                if token != prev_token and token != self.blank_idx:
                    collapsed.append(token)
                prev_token = token
            decoded_batch.append(collapsed)
            
        return decoded_batch
