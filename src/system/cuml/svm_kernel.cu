#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <iostream>
#include <vector>

// OMNI System Layer: C++ CUDA SVM Kernel for cuML Integration
// Strictly Zero-Mock, production-grade memory operations.

extern "C" {

__global__ void RBFKernelCompute(const float* X, const float* Y, float* output, int n_samples_X, int n_samples_Y, int n_features, float gamma) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    int j = blockIdx.y * blockDim.y + threadIdx.y;

    if (i < n_samples_X && j < n_samples_Y) {
        float sum = 0.0f;
        for (int k = 0; k < n_features; ++k) {
            float diff = X[i * n_features + k] - Y[j * n_features + k];
            sum += diff * diff;
        }
        output[i * n_samples_Y + j] = expf(-gamma * sum);
    }
}

// OMNI FFI Interface
void compute_rbf_kernel_cuda(const float* host_X, const float* host_Y, float* host_output, int n_samples_X, int n_samples_Y, int n_features, float gamma) {
    float *d_X, *d_Y, *d_output;
    size_t size_X = n_samples_X * n_features * sizeof(float);
    size_t size_Y = n_samples_Y * n_features * sizeof(float);
    size_t size_out = n_samples_X * n_samples_Y * sizeof(float);

    cudaMalloc((void**)&d_X, size_X);
    cudaMalloc((void**)&d_Y, size_Y);
    cudaMalloc((void**)&d_output, size_out);

    cudaMemcpy(d_X, host_X, size_X, cudaMemcpyHostToDevice);
    cudaMemcpy(d_Y, host_Y, size_Y, cudaMemcpyHostToDevice);

    dim3 threadsPerBlock(16, 16);
    dim3 numBlocks((n_samples_X + threadsPerBlock.x - 1) / threadsPerBlock.x,
                   (n_samples_Y + threadsPerBlock.y - 1) / threadsPerBlock.y);

    RBFKernelCompute<<<numBlocks, threadsPerBlock>>>(d_X, d_Y, d_output, n_samples_X, n_samples_Y, n_features, gamma);
    cudaDeviceSynchronize();

    cudaMemcpy(host_output, d_output, size_out, cudaMemcpyDeviceToHost);

    cudaFree(d_X);
    cudaFree(d_Y);
    cudaFree(d_output);
}

} // extern "C"
