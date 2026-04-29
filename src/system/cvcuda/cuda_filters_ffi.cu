#include <cuda_runtime.h>
#include <iostream>

extern "C" {

    struct OmniCudaResult {
        void* data;
        size_t size;
        const char* error;
    };

    void omni_free_cuda_result(OmniCudaResult* res) {
        if (res) {
            if (res->data) cudaFree(res->data);
            delete res;
        }
    }

    __global__ void rgb_to_grayscale_kernel(const unsigned char* d_rgb, unsigned char* d_gray, int numPixels) {
        int idx = blockIdx.x * blockDim.x + threadIdx.x;
        if (idx < numPixels) {
            int rgb_idx = idx * 3;
            // standard luminosity method
            unsigned char r = d_rgb[rgb_idx];
            unsigned char g = d_rgb[rgb_idx + 1];
            unsigned char b = d_rgb[rgb_idx + 2];
            d_gray[idx] = (unsigned char)(0.299f * r + 0.587f * g + 0.114f * b);
        }
    }

    OmniCudaResult* execute_rgb_to_gray_cuda(const unsigned char* h_rgb, int width, int height) {
        OmniCudaResult* result = new OmniCudaResult{nullptr, 0, nullptr};
        int numPixels = width * height;
        size_t rgbSize = numPixels * 3 * sizeof(unsigned char);
        size_t graySize = numPixels * sizeof(unsigned char);

        unsigned char *d_rgb = nullptr, *d_gray = nullptr;

        cudaError_t err = cudaMalloc((void**)&d_rgb, rgbSize);
        if (err != cudaSuccess) { result->error = "CUDA Malloc failed for RGB"; return result; }

        err = cudaMalloc((void**)&d_gray, graySize);
        if (err != cudaSuccess) { cudaFree(d_rgb); result->error = "CUDA Malloc failed for Gray"; return result; }

        cudaMemcpy(d_rgb, h_rgb, rgbSize, cudaMemcpyHostToDevice);

        int blockSize = 256;
        int numBlocks = (numPixels + blockSize - 1) / blockSize;

        rgb_to_grayscale_kernel<<<numBlocks, blockSize>>>(d_rgb, d_gray, numPixels);
        cudaDeviceSynchronize();

        result->data = d_gray; // returning device pointer for pipelined operations
        result->size = graySize;
        cudaFree(d_rgb);

        return result;
    }
}
