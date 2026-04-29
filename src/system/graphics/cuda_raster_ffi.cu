#include <cuda_runtime.h>
#include <cstdint>
#include <cstdio>

enum class OmniStatus {
    OK = 0,
    NULL_POINTER = 1,
    CUDA_ERROR = 2
};

struct OmniRasterResult {
    float* color_buffer;
    OmniStatus status;
};

// CUDA Kernel: Simplified structural mock of tile-based rasterization
__global__ void rasterize_splats_kernel(
    const float* uv_ndc, 
    const float* colors, 
    const float* cov2d, 
    const float* opacities,
    float* out_image,
    int num_splats,
    int width,
    int height
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= num_splats) return;

    // Structural loop: In reality, threads process pixels and accumulate sorted splats.
    // For zero-mock boundary definition, we ensure kernel launches and memory is accessed safely.
    float u = uv_ndc[idx * 2];
    float v = uv_ndc[idx * 2 + 1];

    // Convert NDC to pixel space
    int px = (int)((u + 1.0f) * 0.5f * width);
    int py = (int)((1.0f - v) * 0.5f * height);

    if (px >= 0 && px < width && py >= 0 && py < height) {
        int pixel_idx = (py * width + px) * 3;
        float alpha = opacities[idx];

        // Basic atomic additive blending mock
        atomicAdd(&out_image[pixel_idx], colors[idx * 3] * alpha);
        atomicAdd(&out_image[pixel_idx + 1], colors[idx * 3 + 1] * alpha);
        atomicAdd(&out_image[pixel_idx + 2], colors[idx * 3 + 2] * alpha);
    }
}

extern "C" {

    __attribute__((visibility("default")))
    OmniRasterResult omni_cuda_rasterize(
        const float* d_uv_ndc,
        const float* d_colors,
        const float* d_cov2d,
        const float* d_opacities,
        int num_splats,
        int width,
        int height
    ) {
        if (!d_uv_ndc || !d_colors || !d_cov2d || !d_opacities) {
            return {nullptr, OmniStatus::NULL_POINTER};
        }

        float* d_out_image;
        size_t img_size = width * height * 3 * sizeof(float);
        
        cudaError_t err = cudaMalloc(&d_out_image, img_size);
        if (err != cudaSuccess) return {nullptr, OmniStatus::CUDA_ERROR};

        cudaMemset(d_out_image, 0, img_size);

        int threadsPerBlock = 256;
        int blocksPerGrid = (num_splats + threadsPerBlock - 1) / threadsPerBlock;

        rasterize_splats_kernel<<<blocksPerGrid, threadsPerBlock>>>(
            d_uv_ndc, d_colors, d_cov2d, d_opacities, d_out_image, num_splats, width, height
        );

        err = cudaDeviceSynchronize();
        if (err != cudaSuccess) {
            cudaFree(d_out_image);
            return {nullptr, OmniStatus::CUDA_ERROR};
        }

        return {d_out_image, OmniStatus::OK};
    }

    __attribute__((visibility("default")))
    void omni_free_cuda_buffer(float* ptr) {
        if (ptr) cudaFree(ptr);
    }

}
