// OMNI System — CUDA FP8 Quantized GEMM Kernel
// E4M3 FP8 matrix multiplication for Hopper GPUs.

#include <cuda_fp8.h>
#include <cuda_runtime.h>
#include <stdio.h>

#define BLOCK_M 128
#define BLOCK_N 128
#define BLOCK_K 64
#define WARP_SIZE 32

// FP8 E4M3 GEMM kernel
__global__ void fp8_gemm_kernel(
    const __nv_fp8_e4m3* __restrict__ A,
    const __nv_fp8_e4m3* __restrict__ B,
    float* __restrict__ C,
    const float scale_a,
    const float scale_b,
    const int M, const int N, const int K
) {
    int row = blockIdx.y * BLOCK_M + threadIdx.y;
    int col = blockIdx.x * BLOCK_N + threadIdx.x;

    if (row >= M || col >= N) return;

    float acc = 0.0f;

    for (int k = 0; k < K; k += BLOCK_K) {
        int k_end = min(k + BLOCK_K, K);

        for (int kk = k; kk < k_end; kk++) {
            float a_val = (float)A[row * K + kk] * scale_a;
            float b_val = (float)B[kk * N + col] * scale_b;
            acc += a_val * b_val;
        }
    }

    C[row * N + col] = acc;
}

// Quantize FP32 to FP8 E4M3
__global__ void quantize_to_fp8(
    const float* __restrict__ input,
    __nv_fp8_e4m3* __restrict__ output,
    float* __restrict__ scale,
    int n
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) return;

    // Per-tensor scale
    float s = *scale;
    float val = input[idx] / s;
    output[idx] = (__nv_fp8_e4m3)val;
}

// Host function for FP8 GEMM
extern "C" void omni_fp8_gemm(
    const void* A_fp8, const void* B_fp8,
    float* C, float scale_a, float scale_b,
    int M, int N, int K
) {
    dim3 block(16, 16);
    dim3 grid((N + block.x - 1) / block.x, (M + block.y - 1) / block.y);

    fp8_gemm_kernel<<<grid, block>>>(
        (const __nv_fp8_e4m3*)A_fp8,
        (const __nv_fp8_e4m3*)B_fp8,
        C, scale_a, scale_b, M, N, K
    );

    cudaDeviceSynchronize();
}

// Compute absmax scale for FP8 quantization
__global__ void compute_absmax_scale(const float* input, float* scale, int n) {
    __shared__ float shared_max[256];
    int tid = threadIdx.x;
    int idx = blockIdx.x * blockDim.x + tid;

    float local_max = 0.0f;
    if (idx < n) local_max = fabsf(input[idx]);
    shared_max[tid] = local_max;
    __syncthreads();

    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) shared_max[tid] = fmaxf(shared_max[tid], shared_max[tid + s]);
        __syncthreads();
    }

    if (tid == 0) atomicMax((int*)scale, __float_as_int(shared_max[0]));
}
