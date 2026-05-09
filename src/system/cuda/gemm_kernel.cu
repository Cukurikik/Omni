//=============================================================================
// OMNI SYSTEM LAYER — CUDA GEMM KERNEL (CUDA C++)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Raw CUDA implementation of General Matrix Multiply (GEMM), 
//              the workhorse of Deep Learning operations.
//=============================================================================

#include <cuda_runtime.h>

extern "C" {

#define TILE_SIZE 32

__global__ void gemm_kernel(
    const float* A, const float* B, float* C, 
    int M, int N, int K
) {
    // Block row and column
    int row = blockIdx.y * TILE_SIZE + threadIdx.y;
    int col = blockIdx.x * TILE_SIZE + threadIdx.x;

    // Shared memory for tiling
    __shared__ float sA[TILE_SIZE][TILE_SIZE];
    __shared__ float sB[TILE_SIZE][TILE_SIZE];

    float sum = 0.0f;

    // Loop over tiles
    for (int t = 0; t < (K + TILE_SIZE - 1) / TILE_SIZE; ++t) {
        
        // Load tile into shared memory
        if (row < M && t * TILE_SIZE + threadIdx.x < K) {
            sA[threadIdx.y][threadIdx.x] = A[row * K + t * TILE_SIZE + threadIdx.x];
        } else {
            sA[threadIdx.y][threadIdx.x] = 0.0f;
        }

        if (t * TILE_SIZE + threadIdx.y < K && col < N) {
            sB[threadIdx.y][threadIdx.x] = B[(t * TILE_SIZE + threadIdx.y) * N + col];
        } else {
            sB[threadIdx.y][threadIdx.x] = 0.0f;
        }

        __syncthreads();

        // Multiply tile
        for (int i = 0; i < TILE_SIZE; ++i) {
            sum += sA[threadIdx.y][i] * sB[i][threadIdx.x];
        }

        __syncthreads();
    }

    // Write output
    if (row < M && col < N) {
        C[row * N + col] = sum;
    }
}

void omni_cuda_execute_gemm(
    const float* d_A, const float* d_B, float* d_C, 
    int M, int N, int K
) {
    dim3 threads(TILE_SIZE, TILE_SIZE);
    dim3 blocks((N + TILE_SIZE - 1) / TILE_SIZE, (M + TILE_SIZE - 1) / TILE_SIZE);

    gemm_kernel<<<blocks, threads>>>(d_A, d_B, d_C, M, N, K);
    cudaDeviceSynchronize();
}

} // extern "C"
