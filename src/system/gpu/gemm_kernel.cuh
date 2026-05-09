// OMNI System Layer — CUDA GEMM Kernel for Transformer Linear Layers
// Optimized matrix multiplication for transformer FFN and projections.
// Learned from: NVIDIA CUTLASS, cublas patterns

#pragma once

#include <cuda_runtime.h>
#include <cstdint>

namespace omni {
namespace system {
namespace gemm {

// Tiled GEMM: C = alpha * A @ B + beta * C
// A: (M, K), B: (K, N), C: (M, N)
template <int TILE_M = 32, int TILE_N = 32, int TILE_K = 32>
__global__ void tiled_gemm_kernel(
    const float* __restrict__ A,
    const float* __restrict__ B,
    float* __restrict__ C,
    const int M, const int N, const int K,
    const float alpha, const float beta
) {
    __shared__ float s_A[TILE_M][TILE_K];
    __shared__ float s_B[TILE_K][TILE_N];

    const int row = blockIdx.y * TILE_M + threadIdx.y;
    const int col = blockIdx.x * TILE_N + threadIdx.x;

    float acc = 0.0f;

    for (int t = 0; t < (K + TILE_K - 1) / TILE_K; t++) {
        // Load A tile
        int a_col = t * TILE_K + threadIdx.x;
        if (row < M && a_col < K)
            s_A[threadIdx.y][threadIdx.x] = A[row * K + a_col];
        else
            s_A[threadIdx.y][threadIdx.x] = 0.0f;

        // Load B tile
        int b_row = t * TILE_K + threadIdx.y;
        if (b_row < K && col < N)
            s_B[threadIdx.y][threadIdx.x] = B[b_row * N + col];
        else
            s_B[threadIdx.y][threadIdx.x] = 0.0f;

        __syncthreads();

        for (int k = 0; k < TILE_K; k++) {
            acc += s_A[threadIdx.y][k] * s_B[k][threadIdx.x];
        }
        __syncthreads();
    }

    if (row < M && col < N) {
        C[row * N + col] = alpha * acc + beta * C[row * N + col];
    }
}

// Fused GEMM + GELU activation
template <int TILE = 32>
__global__ void gemm_gelu_kernel(
    const float* __restrict__ A,
    const float* __restrict__ B,
    float* __restrict__ C,
    const int M, const int N, const int K
) {
    __shared__ float s_A[TILE][TILE];
    __shared__ float s_B[TILE][TILE];

    const int row = blockIdx.y * TILE + threadIdx.y;
    const int col = blockIdx.x * TILE + threadIdx.x;
    float acc = 0.0f;

    for (int t = 0; t < (K + TILE - 1) / TILE; t++) {
        int a_col = t * TILE + threadIdx.x;
        int b_row = t * TILE + threadIdx.y;
        s_A[threadIdx.y][threadIdx.x] = (row < M && a_col < K) ? A[row * K + a_col] : 0.0f;
        s_B[threadIdx.y][threadIdx.x] = (b_row < K && col < N) ? B[b_row * N + col] : 0.0f;
        __syncthreads();
        for (int k = 0; k < TILE; k++)
            acc += s_A[threadIdx.y][k] * s_B[k][threadIdx.x];
        __syncthreads();
    }

    if (row < M && col < N) {
        // GELU approximation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        float x = acc;
        float cdf = 0.5f * (1.0f + tanhf(0.7978845608f * (x + 0.044715f * x * x * x)));
        C[row * N + col] = x * cdf;
    }
}

// Launch helpers
inline void launch_gemm(const float* A, const float* B, float* C,
                         int M, int N, int K, float alpha = 1.0f, float beta = 0.0f,
                         cudaStream_t stream = 0) {
    constexpr int TILE = 32;
    dim3 grid((N + TILE - 1) / TILE, (M + TILE - 1) / TILE);
    dim3 block(TILE, TILE);
    tiled_gemm_kernel<TILE, TILE, TILE><<<grid, block, 0, stream>>>(A, B, C, M, N, K, alpha, beta);
}

inline void launch_gemm_gelu(const float* A, const float* B, float* C,
                              int M, int N, int K, cudaStream_t stream = 0) {
    constexpr int TILE = 32;
    dim3 grid((N + TILE - 1) / TILE, (M + TILE - 1) / TILE);
    dim3 block(TILE, TILE);
    gemm_gelu_kernel<TILE><<<grid, block, 0, stream>>>(A, B, C, M, N, K);
}

}  // namespace gemm
}  // namespace system
}  // namespace omni
