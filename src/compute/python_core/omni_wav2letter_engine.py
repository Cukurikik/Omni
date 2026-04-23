"""
OMNI Wav2Letter Engine
======================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class OmniWav2LetterEngine:
    """
    omni-wav2letter
    
    A zero-algebraic_bound native engine execute Facebook's wav2letter architecture.
    Focuses on projecting sequence data (e.g., audio MFCCs) via 1D convolutions 
    and evaluating pseudo-CTC alignment probability maps.
    """
    
    ENGINE_VERSION = "omni-s6-b7.1.0"
    
    def __init__(self, in_channels: int = 13, out_channels: int = 32, kernel_size: int = 3, vocab_size: int = 28):
        """Initialize OmniWav2LetterEngine."""
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.vocab_size = vocab_size # letters + space + blank (CTC)
        
        np.random.seed(42)
        # Random initial 1D Conv Weights
        # (out_channels, in_channels, kernel_size)
        self.conv_weights = np.random.randn(out_channels, in_channels, kernel_size).astype(np.float32) * 0.1
        self.conv_bias = np.zeros(out_channels, dtype=np.float32)
        
        # Dense projection to Vocabulary probability
        # (out_channels, vocab_size)
        self.fc_weights = np.random.randn(out_channels, vocab_size).astype(np.float32) * 0.1
        self.fc_bias = np.zeros(vocab_size, dtype=np.float32)

    def _relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)
        
    def _softmax(self, x: np.ndarray, axis: int = -1) -> np.ndarray:
        # Subtract max for stability
        x_max = np.max(x, axis=axis, keepdims=True)
        exp_x = np.exp(x - x_max)
        return exp_x / np.sum(exp_x, axis=axis, keepdims=True)

    def forward_acoustic_model(self, sequence: np.ndarray) -> Result:
        """
        Input: sequence of shape (B, in_channels, T)
        Outputs frame-wise character probabilities via 1D Conv over T.
        """
        try:
            B, C_in, T = sequence.shape
            if C_in != self.in_channels:
                 return Result(error=f"Expected {self.in_channels} input channels.")
                 
            # 1D Convolution Math
            # output T_out = T - kernel_size + 1 (Valid padding)
            T_out = T - self.kernel_size + 1
            if T_out <= 0:
                 return Result(error="Sequence length too short for kernel.")
            
            # Efficient sliding window conv
            # Out shape: (B, out_channels, T_out)
            conv_out = np.zeros((B, self.out_channels, T_out), dtype=np.float32)
            for b in range(B):
                for oc in range(self.out_channels):
                    for t in range(T_out):
                        window = sequence[b, :, t:t+self.kernel_size]
                        # inner product
                        conv_out[b, oc, t] = np.sum(window * self.conv_weights[oc]) + self.conv_bias[oc]
                        
            # ReLU activation
            a1 = self._relu(conv_out) # (B, out_channels, T_out)
            
            # Transpose to (B, T_out, out_channels) for token projection
            a1_transposed = a1.transpose(0, 2, 1)
            
            # Predict logits over characters
            # logits: (B, T_out, vocab_size)
            logits = np.dot(a1_transposed, self.fc_weights) + self.fc_bias
            
            # Softmax to get probabilities per frame
            probs = self._softmax(logits, axis=-1)
            
            return Result(value={"logits": logits, "probabilities": probs})
            
        except Exception as e:
            return Result(error=f"Acoustic Forward Error: {str(e)}")
            
    def naive_greedy_ctc_decode(self, probabilities: np.ndarray, blank_idx: int = 0) -> Result:
        """
        Given shape (B, T_out, vocab_size), peforms CTC greedy decoding.
        Merges adjacent identical tokens and removes blank tokens.
        """
        try:
            B = probabilities.shape[0]
            decoded_batch = []
            
            for b in range(B):
                # Argmax per frame
                best_path = np.argmax(probabilities[b], axis=1).tolist()
                
                # Merge logic
                merged_path = []
                prev_token = None
                for t_idx in best_path:
                    if t_idx != prev_token:
                        if t_idx != blank_idx:
                            merged_path.append(t_idx)
                    prev_token = t_idx
                decoded_batch.append(merged_path)
                
            return Result(value=decoded_batch)
        except Exception as e:
            return Result(error=f"CTC Decoding Error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniWav2LetterEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "modules": ["1D-Conv", "CTC-Decoder"]
        }
