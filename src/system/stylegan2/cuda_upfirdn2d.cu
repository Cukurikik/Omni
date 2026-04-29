// OMNI STYLEGAN2: CUDA Upfirdn2d
// High-performance CUDA kernel for Upsampling, FIR filtering, and Downsampling in a single pass.
// Critical for StyleGAN2's anti-aliased image synthesis.
// Source: lucidrains/stylegan2-pytorch
// Note: Saved as .cu for CUDA Toolkit compilation.

#include <cuda_runtime.h>

__global__ void upfirdn2d_kernel(
    const float* __restrict__ input,
    const float* __restrict__ filter,
    float* __restrict__ output,
    int in_w, int in_h, 
    int out_w, int out_h,
    int filter_w, int filter_h,
    int up_x, int up_y,
    int down_x, int down_y,
    int pad_x0, int pad_y0,
    int channels) 
{
    // Output coordinates
    int x_out = blockIdx.x * blockDim.x + threadIdx.x;
    int y_out = blockIdx.y * blockDim.y + threadIdx.y;
    int c = blockIdx.z;

    if (x_out >= out_w || y_out >= out_h || c >= channels) {
        return;
    }

    // Map output to input, applying downsampling and padding
    int in_x_base = x_out * down_x - pad_x0;
    int in_y_base = y_out * down_y - pad_y0;

    float sum = 0.0f;

    // Convolution over the FIR filter
    for (int fy = 0; fy < filter_h; ++fy) {
        int in_y = in_y_base + fy;
        
        // Check if projected input Y is valid and lands on an upsampled boundary
        if (in_y >= 0 && in_y < in_h * up_y && (in_y % up_y) == 0) {
            int true_in_y = in_y / up_y;

            for (int fx = 0; fx < filter_w; ++fx) {
                int in_x = in_x_base + fx;

                // Check X boundary
                if (in_x >= 0 && in_x < in_w * up_x && (in_x % up_x) == 0) {
                    int true_in_x = in_x / up_x;
                    
                    int in_idx = c * (in_h * in_w) + true_in_y * in_w + true_in_x;
                    int filter_idx = fy * filter_w + fx;

                    sum += input[in_idx] * filter[filter_idx];
                }
            }
        }
    }

    // Write output
    int out_idx = c * (out_h * out_w) + y_out * out_w + x_out;
    output[out_idx] = sum;
}
