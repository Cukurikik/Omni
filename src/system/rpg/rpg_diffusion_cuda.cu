#include <cuda_runtime.h>
#include <stdint.h>
#include <stdio.h>

// RPG Diffusion Master CUDA kernels
// Recaptioning, Planning, Generating regional multi-diffusion

template <typename T, typename E>
struct OmniResult {
    bool is_ok;
    T value;
    E error;
};

#define MAX_REGIONS 256
#define MAX_CUDA_THREADS 1024

__global__ void rpg_blend_regions_kernel(float* canvas, const float* regions, const float* masks, int width, int height, int num_regions) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int total_pixels = width * height;

    if (idx < total_pixels) {
        float blended_val = 0.0f;
        float total_weight = 0.0f;

        for (int i = 0; i < num_regions; ++i) {
            float weight = masks[i * total_pixels + idx];
            blended_val += regions[i * total_pixels + idx] * weight;
            total_weight += weight;
        }

        if (total_weight > 0.0f) {
            canvas[idx] = blended_val / total_weight;
        }
    }
}

extern "C" OmniResult<bool, uint32_t> rpg_execute_blending(float* d_canvas, const float* d_regions, const float* d_masks, int w, int h, int num_regions) {
    if (num_regions > MAX_REGIONS) {
        return {false, false, 0x11}; // Exceeds region limits
    }

    int total_pixels = w * h;
    int blocks = (total_pixels + MAX_CUDA_THREADS - 1) / MAX_CUDA_THREADS;

    rpg_blend_regions_kernel<<<blocks, MAX_CUDA_THREADS>>>(d_canvas, d_regions, d_masks, w, h, num_regions);
    
    cudaError_t err = cudaDeviceSynchronize();
    if (err != cudaSuccess) {
        return {false, false, (uint32_t)err};
    }

    return {true, true, 0};
}
