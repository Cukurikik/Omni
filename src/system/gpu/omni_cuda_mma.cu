// OMNI Scientific & HPC Layer
// CUDA C++ matrix multiply-accumulate utilizing hardware Tensor Cores.
// Requires SM_75 (Turing) or higher architecture.

#include <cuda_fp16.h>
#include <mma.h>
#include <iostream>

using namespace nvcuda;

// Dimensions for the Tensor Core operations
const int WMMA_M = 16;
const int WMMA_N = 16;
const int WMMA_K = 16;

__global__ void omni_tensor_core_gemm(half *a, half *b, float *c, int M, int N, int K) {
    // Determine the tile of the matrix this warp will compute
    int warpM = (blockIdx.x * blockDim.x + threadIdx.x) / warpSize;
    int warpN = (blockIdx.y * blockDim.y + threadIdx.y);

    // Fragments for matrix multiplication
    wmma::fragment<wmma::matrix_a, WMMA_M, WMMA_N, WMMA_K, half, wmma::row_major> a_frag;
    wmma::fragment<wmma::matrix_b, WMMA_M, WMMA_N, WMMA_K, half, wmma::col_major> b_frag;
    wmma::fragment<wmma::accumulator, WMMA_M, WMMA_N, WMMA_K, float> c_frag;

    wmma::fill_fragment(c_frag, 0.0f);

    // Loop over the K dimension
    for (int i = 0; i < K; i += WMMA_K) {
        int aRow = warpM * WMMA_M;
        int aCol = i;
        int bRow = i;
        int bCol = warpN * WMMA_N;

        // Bounds check required for incomplete tiles, simplified here for aligned dimensions
        if (aRow < M && aCol < K && bRow < K && bCol < N) {
            wmma::load_matrix_sync(a_frag, a + aRow * K + aCol, K);
            wmma::load_matrix_sync(b_frag, b + bRow * N + bCol, N);

            // Matrix Multiply-Accumulate
            wmma::mma_sync(c_frag, a_frag, b_frag, c_frag);
        }
    }

    // Store the result back to global memory
    int cRow = warpM * WMMA_M;
    int cCol = warpN * WMMA_N;

    if (cRow < M && cCol < N) {
        wmma::store_matrix_sync(c + cRow * N + cCol, c_frag, N, wmma::mem_row_major);
    }
}
