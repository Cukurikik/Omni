//=============================================================================
// OMNI SYSTEM LAYER — CUDA ACTIVATION KERNELS (CUDA C++)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Fast GPU implementations for SwiGLU and GeLU activations, 
//              crucial for modern LLMs and Differential Transformers.
//=============================================================================

#include <cuda_runtime.h>
#include <math.h>

extern "C" {

#define BLOCK_SIZE 256

// Helper: Sigmoid
__device__ inline float sigmoid(float x) {
    return 1.0f / (1.0f + expf(-x));
}

// SwiGLU: Swish(x * W1) * (x * W2)
__global__ void swiglu_kernel(
    float* out, const float* x, const float* w1, const float* w2, 
    int num_elements, float beta
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx < num_elements) {
        float val1 = x[idx] * w1[idx];
        float val2 = x[idx] * w2[idx];
        
        // Swish = x * sigmoid(beta * x)
        float swish = val1 * sigmoid(beta * val1);
        
        out[idx] = swish * val2;
    }
}

// GeLU (Gaussian Error Linear Unit)
__global__ void gelu_kernel(float* out, const float* in, int num_elements) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx < num_elements) {
        float x = in[idx];
        // Approximation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        float cube = x * x * x;
        float inner = 0.7978845608f * (x + 0.044715f * cube);
        out[idx] = 0.5f * x * (1.0f + tanhf(inner));
    }
}

void omni_cuda_execute_swiglu(
    float* d_out, const float* d_x, const float* d_w1, const float* d_w2, 
    int num_elements, float beta
) {
    dim3 grid((num_elements + BLOCK_SIZE - 1) / BLOCK_SIZE);
    dim3 block(BLOCK_SIZE);
    
    swiglu_kernel<<<grid, block>>>(d_out, d_x, d_w1, d_w2, num_elements, beta);
    cudaDeviceSynchronize();
}

void omni_cuda_execute_gelu(float* d_out, const float* d_in, int num_elements) {
    dim3 grid((num_elements + BLOCK_SIZE - 1) / BLOCK_SIZE);
    dim3 block(BLOCK_SIZE);
    
    gelu_kernel<<<grid, block>>>(d_out, d_in, num_elements);
    cudaDeviceSynchronize();
}

} // extern "C"
