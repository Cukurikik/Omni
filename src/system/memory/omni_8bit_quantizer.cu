/*
 * omni_8bit_quantizer.cu — 8-Bit Matrix Quantization Kernel
 * Layer: System / Memory / CUDA
 * Inspired by: TimDettmers/bitsandbytes
 *
 * Implements a CUDA kernel for absolute maximum (absmax) 8-bit quantization.
 * Projects 32-bit floats into signed 8-bit integers while preserving
 * the scale factor needed for dequantization. Zero mock.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <math.h>

// CUDA Kernel: Find maximum absolute value in an array block (Warp reduction usually better, this is block naive)
__global__ void absmax_kernel(const float* input, float* max_out, int n) {
    extern __shared__ float sdata[];
    
    unsigned int tid = threadIdx.x;
    unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    
    sdata[tid] = (i < n) ? fabsf(input[i]) : 0.0f;
    __syncthreads();
    
    // Reduction in shared memory
    for (unsigned int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) {
            if (sdata[tid + s] > sdata[tid]) {
                sdata[tid] = sdata[tid + s];
            }
        }
        __syncthreads();
    }
    
    if (tid == 0) {
        max_out[blockIdx.x] = sdata[0];
    }
}

// CUDA Kernel: Quantize FP32 to INT8 using the computed absmax
__global__ void quantize_8bit_kernel(const float* input, int8_t* output, float absmax, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        float val = input[i];
        // Scale to [-127, 127]
        float scaled = (val / absmax) * 127.0f;
        // Round to nearest integer
        output[i] = (int8_t)roundf(scaled);
    }
}

extern "C" {
    // Host wrapper function to be called via FFI (e.g., from Python/Rust)
    void omni_quantize_8bit_absmax(const float* d_input, int8_t* d_output, float* d_absmax, int n) {
        int threadsPerBlock = 256;
        int blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock;
        
        // 1. Find absmax per block
        float* d_block_maxes;
        cudaMalloc(&d_block_maxes, blocksPerGrid * sizeof(float));
        
        absmax_kernel<<<blocksPerGrid, threadsPerBlock, threadsPerBlock * sizeof(float)>>>(d_input, d_block_maxes, n);
        cudaDeviceSynchronize();
        
        // 2. Find global absmax (running a single block reduction on the block maxes)
        // For simplicity in this native code, we assume blocksPerGrid <= 256.
        absmax_kernel<<<1, 256, 256 * sizeof(float)>>>(d_block_maxes, d_absmax, blocksPerGrid);
        cudaDeviceSynchronize();
        
        // Retrieve global absmax to host to pass to quantize kernel
        float h_absmax;
        cudaMemcpy(&h_absmax, d_absmax, sizeof(float), cudaMemcpyDeviceToHost);
        if (h_absmax == 0.0f) h_absmax = 1e-9f; // Prevent div zero

        // 3. Quantize
        quantize_8bit_kernel<<<blocksPerGrid, threadsPerBlock>>>(d_input, d_output, h_absmax, n);
        cudaDeviceSynchronize();
        
        cudaFree(d_block_maxes);
    }
}
