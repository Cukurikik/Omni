"""
omni_int8_quant.py — INT8 Tensor Quantization
Layer: Compute / AI

Implements symmetric INT8 quantization and dequantization for model weights
and activations to reduce memory bandwidth and increase inference speed.
"""

import torch

def quantize_symmetric(tensor: torch.Tensor, num_bits: int = 8) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Quantizes a floating-point tensor to a symmetric integer representation.
    Returns the quantized tensor and the scale factor.
    """
    qmin = -(2 ** (num_bits - 1))
    qmax = (2 ** (num_bits - 1)) - 1
    
    # Calculate scale factor
    max_val = torch.max(torch.abs(tensor))
    scale = max_val / qmax
    
    # Prevent division by zero
    scale = torch.clamp(scale, min=1e-8)
    
    # Quantize
    q_tensor = torch.round(tensor / scale)
    q_tensor = torch.clamp(q_tensor, qmin, qmax).to(torch.int8)
    
    return q_tensor, scale

def dequantize_symmetric(q_tensor: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    """
    Dequantizes an INT8 tensor back to floating point using the scale factor.
    """
    return q_tensor.float() * scale

class OmniQuantizedLinear(torch.nn.Module):
    """
    A linear layer that stores its weights in INT8 and performs 
    quantized matrix multiplication.
    """
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # Placeholder for INT8 weights and FP32 scale
        self.register_buffer('q_weight', torch.zeros((out_features, in_features), dtype=torch.int8))
        self.register_buffer('w_scale', torch.ones(1))
        
        if bias:
            self.bias = torch.nn.Parameter(torch.zeros(out_features))
        else:
            self.register_parameter('bias', None)

    def pack_weights(self, weight: torch.Tensor):
        """Converts an FP32 weight tensor to INT8 and stores it."""
        q_w, scale = quantize_symmetric(weight)
        self.q_weight.copy_(q_w)
        self.w_scale.copy_(scale)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Dynamically quantizes input, performs integer matmul, and dequantizes.
        In a true highly-optimized environment, this invokes a custom CUDA INT8 kernel.
        """
        # Dynamic quantization of activations
        q_x, x_scale = quantize_symmetric(x)
        
        # INT8 Matmul (PyTorch mock simulation of low-level FBGEMM/CUTLASS)
        # We must cast to float for standard PyTorch matmul if no int8 kernel is available
        out = torch.matmul(q_x.float(), self.q_weight.t().float())
        
        # Dequantize (Scale = Input_Scale * Weight_Scale)
        out = out * (x_scale * self.w_scale)
        
        if self.bias is not None:
            out += self.bias
            
        return out
