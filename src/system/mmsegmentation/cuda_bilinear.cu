// OMNI MMSEGMENTATION: CUDA Bilinear Interpolation
// High-performance GPU kernel to upscale semantic masks (e.g. from 1/4th resolution back to image size).
// Source: open-mmlab/mmsegmentation
// Note: Saved as .cu for CUDA Toolkit compilation.

#include <cuda_runtime.h>

// CUDA Kernel for bilinear interpolation of a 2D float tensor
__global__ void bilinear_interpolate_kernel(
    const float* __restrict__ input,
    float* __restrict__ output,
    int in_height,
    int in_width,
    int out_height,
    int out_width,
    int channels) 
{
    // Global thread coordinates mapping to the OUTPUT tensor
    int x_out = blockIdx.x * blockDim.x + threadIdx.x;
    int y_out = blockIdx.y * blockDim.y + threadIdx.y;
    int c = blockIdx.z * blockDim.z + threadIdx.z;

    if (x_out >= out_width || y_out >= out_height || c >= channels) {
        return;
    }

    // Scale factors
    float scale_x = (float)in_width / out_width;
    float scale_y = (float)in_height / out_height;

    // Map output coordinate to input coordinate
    float x_in = (x_out + 0.5f) * scale_x - 0.5f;
    float y_in = (y_out + 0.5f) * scale_y - 0.5f;

    // Boundary clamping
    x_in = max(0.0f, min(x_in, (float)in_width - 1.0f));
    y_in = max(0.0f, min(y_in, (float)in_height - 1.0f));

    int x1 = (int)floorf(x_in);
    int y1 = (int)floorf(y_in);
    int x2 = min(x1 + 1, in_width - 1);
    int y2 = min(y1 + 1, in_height - 1);

    // Interpolation weights
    float dx = x_in - x1;
    float dy = y_in - y1;

    // Base indices for the input tensor [C, H, W]
    int c_offset = c * in_height * in_width;
    
    float val_tl = input[c_offset + y1 * in_width + x1];
    float val_tr = input[c_offset + y1 * in_width + x2];
    float val_bl = input[c_offset + y2 * in_width + x1];
    float val_br = input[c_offset + y2 * in_width + x2];

    // Bilinear math
    float top = val_tl * (1.0f - dx) + val_tr * dx;
    float bottom = val_bl * (1.0f - dx) + val_br * dx;
    float interpolated = top * (1.0f - dy) + bottom * dy;

    // Write to output tensor
    int out_idx = c * (out_height * out_width) + y_out * out_width + x_out;
    output[out_idx] = interpolated;
}
