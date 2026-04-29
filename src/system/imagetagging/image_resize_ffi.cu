// OMNI SYSTEM LAYER: Image Tagging (CUDA)
// Ultra-fast GPU-based bilinear image resizing and normalization.

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

extern "C" {

    __global__ void resize_normalize_kernel(
        const unsigned char* __restrict__ input,
        int in_w, int in_h,
        float* __restrict__ output,
        int out_w, int out_h)
    {
        int x = blockIdx.x * blockDim.x + threadIdx.x;
        int y = blockIdx.y * blockDim.y + threadIdx.y;

        if (x >= out_w || y >= out_h) return;

        // Bilinear interpolation math
        float x_ratio = (float)(in_w - 1) / out_w;
        float y_ratio = (float)(in_h - 1) / out_h;

        float in_x = x * x_ratio;
        float in_y = y * y_ratio;

        int x0 = (int)in_x;
        int y0 = (int)in_y;
        int x1 = min(x0 + 1, in_w - 1);
        int y1 = min(y0 + 1, in_h - 1);

        float x_diff = in_x - x0;
        float y_diff = in_y - y0;

        // Process 3 channels (RGB)
        for (int c = 0; c < 3; ++c) {
            float p00 = input[(y0 * in_w + x0) * 3 + c];
            float p10 = input[(y0 * in_w + x1) * 3 + c];
            float p01 = input[(y1 * in_w + x0) * 3 + c];
            float p11 = input[(y1 * in_w + x1) * 3 + c];

            float val = p00 * (1 - x_diff) * (1 - y_diff) +
                        p10 * x_diff * (1 - y_diff) +
                        p01 * (1 - x_diff) * y_diff +
                        p11 * x_diff * y_diff;

            // ImageNet normalization: (val/255.0 - mean) / std
            const float means[3] = {0.485f, 0.456f, 0.406f};
            const float stds[3] = {0.229f, 0.224f, 0.225f};
            
            val = (val / 255.0f - means[c]) / stds[c];

            // NCHW format
            output[(c * out_h + y) * out_w + x] = val;
        }
    }

    int omni_cuda_resize_image(const unsigned char* d_input, int in_w, int in_h, float* d_output, int out_w, int out_h) {
        dim3 threads(16, 16);
        dim3 blocks((out_w + threads.x - 1) / threads.x, (out_h + threads.y - 1) / threads.y);

        resize_normalize_kernel<<<blocks, threads>>>(d_input, in_w, in_h, d_output, out_w, out_h);
        
        cudaError_t err = cudaGetLastError();
        if (err != cudaSuccess) return -1;
        
        cudaDeviceSynchronize();
        return 0; // Success
    }
}
