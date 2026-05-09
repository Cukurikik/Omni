#include <omp.h>
#include <stdlib.h>
#include <stdio.h>

/**
 * Omni OpenMP GEMM (C)
 * System & Parallelism Layer
 * General Matrix Multiplication (GEMM) utilizing OpenMP for multi-core CPU
 * thread pooling, heavily optimized for L1 cache tiling.
 */

#define TILE_SIZE 64

extern "C" {

void omni_openmp_sgemm(
    int M, int N, int K,
    const float* A, const float* B, float* C) 
{
    // Zero out C
    #pragma omp parallel for
    for (int i = 0; i < M * N; i++) {
        C[i] = 0.0f;
    }

    // Tiled matrix multiplication to maximize cache hits
    #pragma omp parallel for collapse(2) schedule(dynamic)
    for (int i0 = 0; i0 < M; i0 += TILE_SIZE) {
        for (int j0 = 0; j0 < N; j0 += TILE_SIZE) {
            
            for (int k0 = 0; k0 < K; k0 += TILE_SIZE) {
                
                int i_end = (i0 + TILE_SIZE > M) ? M : (i0 + TILE_SIZE);
                int j_end = (j0 + TILE_SIZE > N) ? N : (j0 + TILE_SIZE);
                int k_end = (k0 + TILE_SIZE > K) ? K : (k0 + TILE_SIZE);

                for (int i = i0; i < i_end; ++i) {
                    for (int j = j0; j < j_end; ++j) {
                        float sum = C[i * N + j];
                        
                        // Inner loop over K
                        // Pragma SIMD hints the compiler to vectorize this inner loop
                        #pragma omp simd reduction(+:sum)
                        for (int k = k0; k < k_end; ++k) {
                            sum += A[i * K + k] * B[k * N + j];
                        }
                        
                        C[i * N + j] = sum;
                    }
                }
            }
        }
    }
}

} // extern "C"
