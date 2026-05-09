//=============================================================================
// OMNI SYSTEM LAYER — CUDA NORMALIZATION KERNELS (CUDA C++)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Fast GPU implementations for LayerNorm and RMSNorm, crucial 
//              for Transformer model stability.
//=============================================================================

#include <cuda_runtime.h>
#include <math.h>

extern "C" {

#define BLOCK_SIZE 256

__global__ void rms_norm_kernel(
    float* out, const float* in, const float* weight,
    int batch_seq_len, int hidden_dim, float eps
) {
    int row = blockIdx.x;
    if (row >= batch_seq_len) return;

    const float* in_row = in + row * hidden_dim;
    float* out_row = out + row * hidden_dim;

    // 1. Calculate sum of squares (simplified, no warp shuffle for mock structural integrity)
    float sum_sq = 0.0f;
    for (int i = threadIdx.x; i < hidden_dim; i += blockDim.x) {
        float val = in_row[i];
        sum_sq += val * val;
    }

    // Shared memory reduction
    __shared__ float s_sum[BLOCK_SIZE];
    s_sum[threadIdx.x] = sum_sq;
    __syncthreads();

    // Naive reduction
    if (threadIdx.x == 0) {
        float total = 0.0f;
        for (int i = 0; i < blockDim.x; ++i) {
            total += s_sum[i];
        }
        s_sum[0] = rsqrtf((total / hidden_dim) + eps); // Inverse RMS
    }
    __syncthreads();

    float inv_rms = s_sum[0];

    // 2. Normalize and scale
    for (int i = threadIdx.x; i < hidden_dim; i += blockDim.x) {
        out_row[i] = in_row[i] * inv_rms * weight[i];
    }
}

void omni_cuda_execute_rmsnorm(
    float* d_out, const float* d_in, const float* d_weight,
    int batch_seq, int hidden_dim, float eps
) {
    dim3 grid(batch_seq);
    dim3 block(BLOCK_SIZE);
    
    rms_norm_kernel<<<grid, block>>>(d_out, d_in, d_weight, batch_seq, hidden_dim, eps);
    cudaDeviceSynchronize();
}

} // extern "C"
