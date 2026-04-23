"""OmniConvolutionFilterEngine — Production-grade 2D convolution for image processing.

Implements spatial convolution with configurable kernels (blur, sharpen, edge detect),
padding modes, and stride for matrix-based image filtering.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniConvolutionFilterEngine:
    """Production engine for 2D spatial convolution."""

    ENGINE_VERSION = "1.0.0"

    KERNELS = {
        "blur_3x3": [[1/9, 1/9, 1/9], [1/9, 1/9, 1/9], [1/9, 1/9, 1/9]],
        "sharpen": [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
        "edge_detect": [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]],
        "emboss": [[-2, -1, 0], [-1, 1, 1], [0, 1, 2]],
        "identity": [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
    }

    def convolve(self, matrix: List[List[float]], kernel: List[List[float]],
                 padding: str = "zero", stride: int = 1) -> Result:
        """
        Apply 2D convolution to a matrix.

        Args:
            matrix: Input 2D matrix.
            kernel: Convolution kernel (must be odd-sized square).
            padding: "zero" or "none".
            stride: Convolution stride.

        Returns:
            Result with output matrix and dimensions.
        """
        try:
            if not matrix or not matrix[0]:
                return Err(ValueError("Matrix must be non-empty."))
            if not kernel or not kernel[0]:
                return Err(ValueError("Kernel must be non-empty."))
            kh, kw = len(kernel), len(kernel[0])
            if kh % 2 == 0 or kw % 2 == 0:
                return Err(ValueError("Kernel dimensions must be odd."))
            if stride < 1:
                return Err(ValueError("Stride must be >= 1."))

            rows, cols = len(matrix), len(matrix[0])
            pad_h, pad_w = kh // 2, kw // 2

            if padding == "zero":
                padded = [[0.0] * (cols + 2 * pad_w) for _ in range(rows + 2 * pad_h)]
                for i in range(rows):
                    for j in range(cols):
                        padded[i + pad_h][j + pad_w] = matrix[i][j]
            else:
                padded = matrix
                rows -= kh - 1
                cols -= kw - 1

            p_rows, p_cols = len(padded), len(padded[0])
            out_h = (p_rows - kh) // stride + 1
            out_w = (p_cols - kw) // stride + 1
            output = []

            for i in range(out_h):
                row_out = []
                for j in range(out_w):
                    val = 0.0
                    for ki in range(kh):
                        for kj in range(kw):
                            val += padded[i * stride + ki][j * stride + kj] * kernel[ki][kj]
                    row_out.append(round(val, 6))
                output.append(row_out)

            return Ok({"output": output, "output_shape": [len(output), len(output[0]) if output else 0],
                        "input_shape": [len(matrix), len(matrix[0])], "kernel_shape": [kh, kw],
                        "padding": padding, "stride": stride})
        except Exception as e:
            return Err(e)

    def apply_named_kernel(self, matrix: List[List[float]], kernel_name: str) -> Result:
        """Apply a named kernel from the built-in library."""
        if kernel_name not in self.KERNELS:
            return Err(ValueError(f"Unknown kernel '{kernel_name}'. Available: {list(self.KERNELS.keys())}"))
        return self.convolve(matrix, self.KERNELS[kernel_name])

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniConvolutionFilterEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "built_in_kernels": list(self.KERNELS.keys())}
