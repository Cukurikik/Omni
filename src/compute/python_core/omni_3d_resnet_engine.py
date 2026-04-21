"""
OMNI 3D-ResNet Engine — Spatiotemporal convolution primitives for video understanding.
Assimilated from: kenshohara/3D-ResNets-PyTorch
Provides: 3D convolution, 3D batch normalization, residual block, spatiotemporal pooling.
"""
import numpy as np
from typing import Tuple



ENGINE_VERSION = "1.0.0-omni"

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class Omni3DResNetEngine:
    """
    Pure NumPy 3D convolution engine inspired by 3D-ResNets-PyTorch.

    Implements the core spatiotemporal operations needed for video classification:
      - 3D convolution (naive but correct reference implementation)
      - Batch normalization over 5D tensors (N, C, D, H, W)
      - Residual addition with identity shortcut
      - Global average pooling over spatiotemporal dimensions

    @since 1.0.0
    @tags ["video", "3d-conv", "resnet", "spatiotemporal", "compute"]
    """

    def __init__(self) -> None:
        """Initialize Omni3DResNetEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "3DResNet", "capability": "SpatiotemporalConvolution"})

    def conv3d(
        self,
        input_tensor: np.ndarray,
        kernel: np.ndarray,
        stride: Tuple[int, int, int] = (1, 1, 1),
        padding: Tuple[int, int, int] = (0, 0, 0),
    ) -> Result:
        """
        Performs a single-channel 3D convolution (correlation).

        input:  (D_in, H_in, W_in)
        kernel: (kD, kH, kW)
        output: (D_out, H_out, W_out)

        @param input_tensor: 3D input volume.
        @param kernel: 3D convolution kernel.
        @param stride: (sD, sH, sW) stride in each dimension.
        @param padding: (pD, pH, pW) zero-padding in each dimension.
        @returns Result containing 3D output volume.
        """
        if input_tensor.ndim != 3 or kernel.ndim != 3:
            return Err("Both input and kernel must be 3D.")

        sD, sH, sW = stride
        pD, pH, pW = padding
        kD, kH, kW = kernel.shape

        # Apply zero-padding
        if pD > 0 or pH > 0 or pW > 0:
            padded = np.pad(input_tensor, ((pD, pD), (pH, pH), (pW, pW)), mode='constant')
        else:
            padded = input_tensor

        D_in, H_in, W_in = padded.shape
        D_out = (D_in - kD) // sD + 1
        H_out = (H_in - kH) // sH + 1
        W_out = (W_in - kW) // sW + 1

        if D_out <= 0 or H_out <= 0 or W_out <= 0:
            return Err("Output dimensions are non-positive. Check kernel size vs input + padding.")

        output = np.zeros((D_out, H_out, W_out), dtype=np.float64)

        for d in range(D_out):
            for h in range(H_out):
                for w in range(W_out):
                    region = padded[
                        d * sD:d * sD + kD,
                        h * sH:h * sH + kH,
                        w * sW:w * sW + kW,
                    ]
                    output[d, h, w] = np.sum(region * kernel)

        return Ok(output)

    def batch_norm_5d(
        self,
        tensor: np.ndarray,
        gamma: np.ndarray,
        beta: np.ndarray,
        eps: float = 1e-5,
    ) -> Result:
        """
        Applies batch normalization over a 5D tensor (N, C, D, H, W).

        For each channel c:
          x_hat = (x - mean) / sqrt(var + eps)
          output = gamma[c] * x_hat + beta[c]

        @param tensor: 5D input (batch, channels, depth, height, width).
        @param gamma: 1D scale parameter per channel.
        @param beta: 1D shift parameter per channel.
        @param eps: Numeric stability constant.
        @returns Result containing normalized 5D tensor.
        """
        if tensor.ndim != 5:
            return Err("Input tensor must be 5D (N, C, D, H, W).")
        C = tensor.shape[1]
        if gamma.shape != (C,) or beta.shape != (C,):
            return Err(f"gamma and beta must have shape ({C},).")

        # Compute per-channel statistics over (N, D, H, W)
        mean = np.mean(tensor, axis=(0, 2, 3, 4), keepdims=True)
        var = np.var(tensor, axis=(0, 2, 3, 4), keepdims=True)

        x_hat = (tensor - mean) / np.sqrt(var + eps)

        # Reshape gamma/beta for broadcasting: (1, C, 1, 1, 1)
        g = gamma.reshape(1, C, 1, 1, 1)
        b = beta.reshape(1, C, 1, 1, 1)

        return Ok(g * x_hat + b)

    def residual_add(self, x: np.ndarray, shortcut: np.ndarray) -> Result:
        """
        Residual connection: output = relu(x + shortcut).

        @param x: Main branch output.
        @param shortcut: Identity (or projected) shortcut.
        @returns Result containing element-wise sum followed by ReLU.
        """
        if x.shape != shortcut.shape:
            return Err("Main branch and shortcut must have identical shapes for residual add.")

        return Ok(np.maximum(0, x + shortcut))

    def global_avg_pool_3d(self, tensor: np.ndarray) -> Result:
        """
        Global average pooling over spatiotemporal dimensions (D, H, W).

        Input:  (N, C, D, H, W) or (C, D, H, W)
        Output: (N, C) or (C,)

        @param tensor: 4D or 5D tensor.
        @returns Result containing pooled tensor.
        """
        if tensor.ndim == 5:
            pooled = np.mean(tensor, axis=(2, 3, 4))
        elif tensor.ndim == 4:
            pooled = np.mean(tensor, axis=(1, 2, 3))
        else:
            return Err("Input must be 4D (C, D, H, W) or 5D (N, C, D, H, W).")

        return Ok(pooled)

    def relu(self, x: np.ndarray) -> Result:
        """
        Element-wise ReLU activation: max(0, x).

        @param x: Input array of any shape.
        @returns Result containing activated array.
        """
        return Ok(np.maximum(0, x))
