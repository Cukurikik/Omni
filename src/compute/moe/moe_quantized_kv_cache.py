"""
moe_quantized_kv_cache.py — Int8/FP8 Quantized KV Cache
Layer: Compute / AI — MoE Inference Optimization

Implements per-token, per-channel Int8 quantization for the KV cache.
Since MoE models generate sparsely routed tokens, the KV cache grows
immensely. Quantizing it prevents memory bandwidth bottlenecks during
long-context generation.
"""
import torch
import torch.nn as nn
from typing import Tuple, Optional


class QuantizedKVCache(nn.Module):
    """
    Int8 Quantized KV Cache for MoE models.
    Uses asymmetric per-token quantization.
    """
    def __init__(self, max_batch_size: int, max_seq_len: int, num_heads: int, head_dim: int, device: str = "cuda"):
        super().__init__()
        self.max_batch_size = max_batch_size
        self.max_seq_len = max_seq_len
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.device = torch.device(device)

        # Int8 Storage
        self.register_buffer("k_cache", torch.zeros(
            (max_batch_size, num_heads, max_seq_len, head_dim), 
            dtype=torch.int8, device=self.device
        ))
        self.register_buffer("v_cache", torch.zeros(
            (max_batch_size, num_heads, max_seq_len, head_dim), 
            dtype=torch.int8, device=self.device
        ))

        # Scaling factors (FP16/FP32)
        self.register_buffer("k_scales", torch.zeros(
            (max_batch_size, num_heads, max_seq_len, 1), 
            dtype=torch.float16, device=self.device
        ))
        self.register_buffer("v_scales", torch.zeros(
            (max_batch_size, num_heads, max_seq_len, 1), 
            dtype=torch.float16, device=self.device
        ))
        
        # Zero points (FP16/FP32)
        self.register_buffer("k_zeros", torch.zeros(
            (max_batch_size, num_heads, max_seq_len, 1), 
            dtype=torch.float16, device=self.device
        ))
        self.register_buffer("v_zeros", torch.zeros(
            (max_batch_size, num_heads, max_seq_len, 1), 
            dtype=torch.float16, device=self.device
        ))

    def _quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Asymmetric Int8 quantization."""
        # x: (B, H, S, D)
        x_min = x.min(dim=-1, keepdim=True).values
        x_max = x.max(dim=-1, keepdim=True).values
        
        # Avoid division by zero
        scale = (x_max - x_min) / 255.0
        scale = torch.clamp(scale, min=1e-5)
        
        zero_point = torch.round(-x_min / scale) - 128
        
        q_x = torch.clamp(torch.round(x / scale) + zero_point, -128, 127).to(torch.int8)
        
        return q_x, scale.to(torch.float16), zero_point.to(torch.float16)

    def _dequantize(self, q_x: torch.Tensor, scale: torch.Tensor, zero_point: torch.Tensor) -> torch.Tensor:
        """Dequantize Int8 back to FP16/FP32."""
        # q_x: (..., D), scale: (..., 1), zero_point: (..., 1)
        return (q_x.to(scale.dtype) - zero_point) * scale

    def update(self, k: torch.Tensor, v: torch.Tensor, batch_idx: int, seq_start: int):
        """
        Update the KV cache with new tokens.
        k, v shapes: (1, H, S, D) - usually updating one sequence at a time in generation.
        """
        S = k.size(2)
        seq_end = seq_start + S
        
        if seq_end > self.max_seq_len:
            raise ValueError(f"Sequence length {seq_end} exceeds max {self.max_seq_len}")

        # Quantize new tokens
        q_k, k_scale, k_zero = self._quantize(k)
        q_v, v_scale, v_zero = self._quantize(v)

        # Store in cache
        self.k_cache[batch_idx:batch_idx+1, :, seq_start:seq_end, :] = q_k
        self.v_cache[batch_idx:batch_idx+1, :, seq_start:seq_end, :] = q_v
        
        self.k_scales[batch_idx:batch_idx+1, :, seq_start:seq_end, :] = k_scale
        self.v_scales[batch_idx:batch_idx+1, :, seq_start:seq_end, :] = v_scale
        
        self.k_zeros[batch_idx:batch_idx+1, :, seq_start:seq_end, :] = k_zero
        self.v_zeros[batch_idx:batch_idx+1, :, seq_start:seq_end, :] = v_zero

    def get_kv(self, batch_idx: int, seq_len: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Retrieve dequantized KV up to seq_len."""
        q_k = self.k_cache[batch_idx:batch_idx+1, :, :seq_len, :]
        k_s = self.k_scales[batch_idx:batch_idx+1, :, :seq_len, :]
        k_z = self.k_zeros[batch_idx:batch_idx+1, :, :seq_len, :]
        k_out = self._dequantize(q_k, k_s, k_z)

        q_v = self.v_cache[batch_idx:batch_idx+1, :, :seq_len, :]
        v_s = self.v_scales[batch_idx:batch_idx+1, :, :seq_len, :]
        v_z = self.v_zeros[batch_idx:batch_idx+1, :, :seq_len, :]
        v_out = self._dequantize(q_v, v_s, v_z)

        return k_out, v_out
